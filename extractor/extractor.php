<?
	require_once('sqlite.php');
	
	class DocumentationExtractor
	{
		function __construct($ref)
		{
			$this->dom = null;
			$this->ref = $ref;

			$prefix = '/usr/share/doc/php-doc/html/';
			
			if (is_a($ref, 'ReflectionMethod'))
			{
				$class = $ref->class;
				$name = $ref->name;
				
				$name = preg_replace('/^_+/', '', $name);				
				$filename = $prefix . strtolower($class) . '.' . strtolower($name) . '.html';
			}
			else if (is_a($ref, 'ReflectionFunction'))
			{

				$filename = $prefix . 'function.' . str_replace('_', '-', $ref->getName()) . '.html';
			}
			else
			{
				return;
			}

			$this->dom = new DOMDocument();
			$this->dom->substituteEntities = true;
			$this->dom->preserveWhitespace = false;
			
			if (!@$this->dom->loadHTMLFile($filename))
			{
				$this->dom = null;
			}
			else
			{
				$this->parse();
			}
		}
		
		function documentation_found()
		{
			return $this->dom != null;
		}
		
		function short_description()
		{
			return $this->doc['short_description'];
		}
		
		function description()
		{
			return $this->doc['description'];
		}
		
		function arguments()
		{
			return $this->doc['arguments'];
		}
		
		private function node_text_normalize($text)
		{
			$text = str_replace("\n", ' ', $text);
			return trim(preg_replace('/\s+/', ' ', $text));
		}
		
		private function valid_markup($node, &$tag)
		{
			$markups = array(
				'i' => 'i',
				'b' => 'b',
				'strong' => 'b',
				'em' => 'i'
			);
			
			if (array_key_exists($node->nodeName, $markups))
			{
				$tag = $markups[$node->nodeName];
				return true;
			}
			
			return false;
		}
		
		private function escape($text)
		{
			return htmlentities($text);
		}

		private function node_text($node, $select = null)
		{
			if (is_a($node, 'DOMText'))
			{
				return $this->node_text_normalize($this->escape($node->nodeValue));
			}
			
			$text = '';
			$except = array();
			
			if ($select != null)
			{
				$xpath = new DOMXPath($this->dom);
				$ret = $xpath->query($select, $node);
				
				foreach ($ret as $child)
				{
					$except[] = $child;
				}
			}
			
			foreach ($node->childNodes as $child)
			{
				$exception = false;
				
				foreach ($except as $ex)
				{
					if ($ex->isSameNode($child))
					{
						$exception = true;
						break;
					}
				}
				
				if ($exception)
				{
					continue;
				}

				$node_text = $this->node_text($child);
				$tag = '';
				
				if ($text != '')
				{
					$text .= ' ';
				}
				
				if ($this->valid_markup($child, $tag))
				{
					$text .= '<' . $tag . '>' . $node_text . '</' . $tag . '>';
				}
				else
				{
					$text .= $node_text;
				}
			}
			
			return $this->node_text_normalize($text);
		}
		
		private function extract_text($path, $node = null, $all = false)
		{
			$xpath = new DOMXPath($this->dom);
			$ret = $xpath->query($path, $node !== null ? $node : $this->dom);
			
			if ($ret->length == 0)
			{
				return '';
			}
			
			$text = '';
			
			foreach ($ret as $child)
			{
				$text .= ' ' . $this->node_text($child);
				
				if (!$all)
				{
					break;
				}
			}
			
			return $this->node_text_normalize($text);
		}
		
		function parse_function()
		{
			$this->doc = array(
				'short_description' => $this->extract_text('//span[@class="dc-title"]'),
				'description' => $this->extract_text('//p[@class="para rdfs-comment"]'),
				'arguments' => array()
			);
			
			$xpath = new DOMXPath($this->dom);
			$names = $xpath->query('//div[@class="refsect1 parameters"]/dl/dt');
			$descriptions = $xpath->query('//div[@class="refsect1 parameters"]/dl/dd');
			
			for ($i = 0; $i < $names->length; $i++)
			{
				$name = $this->extract_text('span[@class="term"]//tt[@class="parameter"]', $names->item($i));
				$description = $this->node_text($descriptions->item($i), 'div[@class="example"]|blockquote');
				
				$this->doc['arguments'][] = array('name' => $name, 'description' => $description);
			}
			
			$this->doc['returns'] = $this->extract_text('//div[@class="refsect1 returnvalues"]/p[@class="para"]', null, true);
		}
		
		function parse_class()
		{
			// TODO
		}
		
		function parse()
		{
			if (is_a($this->ref, 'ReflectionFunctionAbstract'))
			{
				$this->parse_function();
			}
			else if (is_a($this->ref, 'ReflectionClass'))
			{
				$this->parse_class();
			}
		}
	};
	
	function insert_function($db, $ref, $classid)
	{
		$extractor = new DocumentationExtractor($ref);
		$short_description = '';
		$description = '';
		$arguments_doc = array();
		
		if ($extractor->documentation_found())
		{
			$short_description = $extractor->short_description();
			$description = $extractor->description();
			$arguments_doc = $extractor->arguments();
		}
		
		$params = array(
			'name' => $ref->getName(), 
			'class' => $classid,
			'short_description' => $short_description,
			'description' => $description
		);
		
		if (is_a($ref, 'ReflectionMethod'))
		{
			if ($ref->isPrivate())
			{
				return;
			}

			$flags = intval($ref->isConstructor()) << 0 |
			         intval($ref->isDestructor()) << 1 |
			         intval($ref->isAbstract()) << 2 |
			         intval($ref->isFinal()) << 3 |
			         intval($ref->isProtected()) << 4 |
			         intval($ref->isPublic()) << 5 |
			         intval($ref->isStatic()) << 6;
			
			$params['flags'] = $flags;
		}

		$db->insert('functions', $params);
		$id = intval($db->last_insert_id());
		
		foreach ($ref->getParameters() as $parameter)
		{
			$description = '';
			
			if ($parameter->getPosition() < count($arguments_doc))
			{
				$description = $arguments_doc[$parameter->getPosition()]['description'];
			}
			
			$db->insert('arguments', array(
				'function' => $id,
				'index' => $parameter->getPosition(),
				'name' => $parameter->getName(),
				'optional' => $parameter->isOptional() ? 1 : 0,
				'default' => $parameter->isDefaultValueAvailable() ? $parameter->getDefaultValue() : '',
				'description' => $description
			));
		}
	}
	
	function insert_property($db, $ref, $classid)
	{
		if ($ref->isPrivate())
		{
			return;
		}

		$doc = $ref->getDocComment();
		
		$flags = intval($ref->isProtected()) << 4 |
		         intval($ref->isPublic()) << 5 |
		         intval($ref->isStatic()) << 6 | 
		         intval($ref->isDefault()) << 7;
		
		$db->insert('properties', array(
			'name' => $ref->getName(),
			'doc' => $doc ? $doc : '',
			'class' => $classid,
			'flags' => $flags
		));
	}
	
	function insert_class($db, $ref)
	{
		$doc = $ref->getDocComment();
		
		$db->insert('classes', array(
			'name' => $ref->getName(), 
			'doc' => $doc ? $doc : '',
			'parent' => 0,
			'interface' => $ref->isInterface() ? 1 : 0
		));
		
		$id = $db->last_insert_id();
		
		foreach ($ref->getMethods() as $method)
		{
			insert_function($db, $method, $id);
		}
		
		foreach ($ref->getProperties() as $property)
		{
			insert_property($db, $property, $id);
		}
		
		foreach ($ref->getConstants() as $name => $value)
		{
			$db->insert('constants', array('name' => $name, 'class' => $id));
		}
	}

	$dbname = 'phpsymbols.db';

	if (file_exists($dbname))
	{
		unlink($dbname);
	}

	$db = new SQLiteDB($dbname);

	$db->query("CREATE TABLE `classes` (`id` INTEGER PRIMARY KEY, `name` STRING, `doc` STRING, `parent` INTEGER, `interface` INTEGER)");
	$db->query("CREATE INDEX `class_name` ON `classes` (`name`)");
	$db->query("CREATE INDEX `class_parent` ON `classes` (`parent`)");
	
	$db->query("CREATE TABLE `interfaces` (`class` INTEGER, `interface` INTEGER)");
	$db->query("CREATE INDEX `interface_class` ON `interfaces` (`class`)");
	$db->query("CREATE INDEX `interface_interface` ON `interfaces` (`interface`)");
	
	$db->query("CREATE TABLE `properties` (`id` INTEGER PRIMARY KEY, `name` STRING, `doc` STRING, `class` INTEGER, `flags` INTEGER)");
	$db->query("CREATE INDEX `property_name` ON `properties` (`name`)");
	$db->query("CREATE INDEX `property_class` ON `properties` (`class`)");
	$db->query("CREATE INDEX `property_flags` ON `properties` (`flags`)");
	
	$db->query("CREATE TABLE `constants` (`id` INTEGER PRIMARY KEY, `name` STRING, `class` INTEGER)");
	$db->query("CREATE INDEX `constant_name` ON `properties` (`name`)");
	
	$db->query("CREATE TABLE `globals` (`id` INTEGER PRIMARY KEY, `name` STRING)");
	$db->query("CREATE INDEX `global_name` ON `properties` (`name`)");

	$db->query("CREATE TABLE `functions` (`id` INTEGER PRIMARY KEY, `name` STRING, `short_description` STRING, `description` STRING, `class` INTEGER, `flags` INTEGER)");
	$db->query("CREATE INDEX `function_name` ON `functions` (`name`)");
	$db->query("CREATE INDEX `function_class` ON `functions` (`class`)");
	$db->query("CREATE INDEX `function_flags` ON `functions` (`flags`)");
	
	$db->query("CREATE TABLE `arguments` (`function` INTEGER, `index` INTEGER, `name` STRING, `optional` INTEGER, `default` STRING, `description` STRING)");
	$db->query("CREATE INDEX `argument_function` ON `arguments` (`function`)");
	$db->query("CREATE INDEX `argument_index` ON `arguments` (`index`)");
	
	/* Iterate over all the classes */
	$classes = get_declared_classes();
	$num = count($classes);
	
	$db->query('BEGIN TRANSACTION');
	
	for ($i = 0; $i < $num; $i++)
	{
		$ref = new ReflectionClass($classes[$i]);
		insert_class($db, $ref);
	}
	
	$interfaces = get_declared_interfaces();
	foreach ($interfaces as $interface)
	{
		$ref = new ReflectionClass($interface);
		insert_class($db, $ref);
	}
	
	for ($i = 0; $i < $num; $i++)
	{
		$ref = new ReflectionClass($classes[$i]);
		
		foreach ($ref->getInterfaces() as $name => $class)
		{
			if ($name == 'Reflector')
			{
				continue;
			}

			$id = $db->query_value('SELECT id FROM classes WHERE name = "' . $name . '"');
			$db->insert('interfaces', array('class' => $i + 1, 'interface' => $id));
		}
		
		$parent = $ref->getParentClass();
		
		if ($parent == null)
		{
			continue;
		}
		
		$id = $db->query_value('SELECT id FROM classes WHERE name = "' . $parent->getName() . '"');
		
		if ($id !== null)
		{
			$db->update('classes', 'id = ' . ($i + 1), array('parent' => $id));
		}
	}

	$funcs = get_defined_functions();
	
	/* Iterate over all the functions */
	$num = count($funcs['internal']);
	for ($i = 0; $i < $num; $i++)
	{
		$ref = new ReflectionFunction($funcs['internal'][$i]);
		insert_function($db, $ref, 0);
	}
	
	$constants = get_defined_constants();
	
	foreach ($constants as $name => $value)
	{
		$db->insert('constants', array('name' => $name, 'class' => 0));
	}
	
	foreach ($GLOBALS as $name => $value)
	{
		if ($name[0] != '_')
		{
			continue;
		}

		$db->insert('globals', array('name' => $name));
	}
	
	$db->query('COMMIT TRANSACTION');
?>
