PUGI__FN xpath_string string_value(const xpath_node& na, xpath_allocator* alloc)
{
	if (na.attribute())
		return xpath_string::from_const(na.attribute().value());
	else
	{
		xml_node n = na.node();

		switch (n.type())
		{
		case node_pcdata:
		case node_cdata:
		case node_comment:
		case node_pi:
			return xpath_string::from_const(n.value());

		case node_document:
		case node_element:
		{
			xpath_string result;

			// element nodes can have value if parse_embed_pcdata was used
			if (n.value()[0])
				result.append(xpath_string::from_const(n.value()), alloc);

			xml_node cur = n.first_child();

			while (cur && cur != n)
			{
				if (cur.type() == node_pcdata || cur.type() == node_cdata)
					result.append(xpath_string::from_const(cur.value()), alloc);

				if (cur.first_child())
					cur = cur.first_child();
				else if (cur.next_sibling())
					cur = cur.next_sibling();
				else
				{
					while (!cur.next_sibling() && cur != n)
						cur = cur.parent();

					if (cur != n) cur = cur.next_sibling();
				}
			}

			return result;
		}

		default:
			return xpath_string();
		}
	}
}
