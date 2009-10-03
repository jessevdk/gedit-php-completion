<?

class SQLiteDB
{
	var $last_result = 0;
	var $resource = 0;
	
	public static function unserialize($item)
	{
		$out = array();
		$cur = '';
		
		for ($i = 0; $i < strlen($item); $i++)
		{
			if ($item[$i] == '\\')
				$i++;
			elseif ($item[$i] == ',')
			{
				$out[] = $cur;
				$cur = null;
				continue;
			}
			
			$cur .= $item[$i];				
		}
		
		if ($cur !== null)
			$out[] = $cur;
		
		return $out;
	}
	
	private function error($assoc = array())
	{
		var_dump($assoc['query']);
		var_dump($this->last_error());
	}
    
	function SQLiteDB($filename)
	{
		if ($filename)
			$this->db_open($filename);
	}

	function db_open($filename)
	{
		if ($filename != NULL)
		{
			$this->resource = new PDO('sqlite:' . $filename);
			
			if (!$this->resource)
			{
				return false;
			}
		}

		return true;
	}
	
	function last_error()
	{
		$error = $this->resource->errorInfo();
		return $error[2];
	}
    
	function query($query)
	{
		if (!$this->resource)
			return;
			
		$handle = $this->resource->query($query);
		
		if ($handle === false)
		{
			$this->error(array('query' => $query));
			return null;
		} 
		else if ($handle !== true)
		{
			$this->last_result = $handle->fetchAll();
			return $this->last_result;        
		}

		return true;
	}
	
	function query_value($query, $idx = 0)
	{
		$result = $this->query_first($query);
		
		if (is_array($result))
			return $result[$idx];
		
		return $result;
	}
    
	function query_first($query)
	{
		$result = $this->query($query);

		if (is_string($result))
			return $result;
		else if (!is_array($result) || count($result) == 0)
			return NULL;
		else
			return $result[0];
	}
    
	function close()
	{
		if ($this->resource)
		{
			$this->resource = null;
		}
	}
	
	function serialize($item)
	{
		if (!is_array($item))
			return $item;
		
		$result = array();
		
		foreach ($item as $i)
			$result[] = str_replace(',', '\,', str_replace("\\", "\\\\", $i));
		
		return $this->quote(implode(', ', $result));
	}
    
	function insert($table, $vals, $literals = array())
	{
		if (!$this->resource)
			return;

		$query = 'INSERT INTO `' . $table . '`';
		$keys = array_keys($vals);

		$k = "(";
		$v = "VALUES(";

		for ($i = 0; $i < count($keys); $i++)
		{
			if ($i != 0)
			{
				$k .= ', ';
				$v .= ', ';
			}

			$k .= '`' . $keys[$i] . '`';

			if (is_string($vals[$keys[$i]]) && !in_array($keys[$i], $literals))
				$v .= $this->quote($vals[$keys[$i]]);
			elseif ($vals[$keys[$i]] === null)
				$v .= 'null';
			else
				$v .= $this->serialize($vals[$keys[$i]]);
		}

		$query = $query . ' ' . $k . ') ' . $v . ');';
		return $this->query($query);
	}
    
	function last_insert_id()
	{
		if (!$this->resource)
			return 0;

		return $this->resource->lastInsertId();
	}
    
	function delete($table, $condition, $limit = 1)
	{
		if (!$this->resource)
			return;

		$this->query('DELETE FROM `' . $table . '` ' . ($condition ? ('WHERE ' . $condition . ' ') : '') . ($limit > 0 ? ('LIMIT ' . $limit) : ''));
	}
    
	function update($table, $condition, $vals, $literals = array())
	{
		if (!$this->resource)
			return;

		$query = 'UPDATE `' . $table . '` SET ';
		$keys = array_keys($vals);
		$k = "";

		for ($i = 0; $i < count($keys); $i++) {
			if ($i != 0)
				$k .= ', ';

			$k .= '`' . $keys[$i] . "` = ";

			if (is_string($vals[$keys[$i]]) && !in_array($keys[$i], $literals))
				$k .= $this->quote($vals[$keys[$i]]);
			elseif ($vals[$keys[$i]] === null)
				$k .= 'null';
			else
				$k .= $this->serialize($vals[$keys[$i]]);
		}

		$query .= $k;

		if ($condition)
			$query .= ' WHERE ' . $condition;

		return $this->query($query);
	}
	
	function quote($s)
	{
		return $this->resource->quote($s);
	}
}
?>
