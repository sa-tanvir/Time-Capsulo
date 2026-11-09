PUGI__FN char_t* strconv_escape(char_t* s, gap& g)
{
	char_t* stre = s + 1;

	switch (*stre)
	{
		case '#':	// &#...
		{
			unsigned int ucsc = 0;

			if (stre[1] == 'x') // &#x... (hex code)
			{
				stre += 2;

				char_t ch = *stre;

				if (ch == ';') return stre;

				for (;;)
				{
					if (static_cast<unsigned int>(ch - '0') <= 9)
						ucsc = 16 * ucsc + (ch - '0');
					else if (static_cast<unsigned int>((ch | ' ') - 'a') <= 5)
						ucsc = 16 * ucsc + ((ch | ' ') - 'a' + 10);
					else if (ch == ';')
						break;
					else // cancel
						return stre;

					ch = *++stre;
				}

				++stre;
			}
			else	// &#... (dec code)
			{
				char_t ch = *++stre;

				if (ch == ';') return stre;

				for (;;)
				{
					if (static_cast<unsigned int>(ch - '0') <= 9)
						ucsc = 10 * ucsc + (ch - '0');
					else if (ch == ';')
						break;
					else // cancel
						return stre;

					ch = *++stre;
				}

				++stre;
			}

		#ifdef PUGIXML_WCHAR_MODE
			s = reinterpret_cast<char_t*>(wchar_writer::any(reinterpret_cast<wchar_writer::value_type>(s), ucsc));
		#else
			s = reinterpret_cast<char_t*>(utf8_writer::any(reinterpret_cast<uint8_t*>(s), ucsc));
		#endif

			g.push(s, stre - s);
			return stre;
		}

		case 'a':	// &a
		{
			++stre;

			if (*stre == 'm') // &am
			{
				if (*++stre == 'p' && *++stre == ';') // &amp;
				{
					*s++ = '&';
					++stre;

					g.push(s, stre - s);
					return stre;
				}
			}
			else if (*stre == 'p') // &ap
			{
				if (*++stre == 'o' && *++stre == 's' && *++stre == ';') // &apos;
				{
					*s++ = '\'';
					++stre;

					g.push(s, stre - s);
					return stre;
				}
			}
			break;
		}

		case 'g': // &g
		{
			if (*++stre == 't' && *++stre == ';') // &gt;
			{
				*s++ = '>';
				++stre;

				g.push(s, stre - s);
				return stre;
			}
			break;
		}

		case 'l': // &l
		{
			if (*++stre == 't' && *++stre == ';') // &lt;
			{
				*s++ = '<';
				++stre;

				g.push(s, stre - s);
				return stre;
			}
			break;
		}

		case 'q': // &q
		{
			if (*++stre == 'u' && *++stre == 'o' && *++stre == 't' && *++stre == ';') // &quot;
			{
				*s++ = '"';
				++stre;

				g.push(s, stre - s);
				return stre;
			}
			break;
		}

		default:
			break;
	}

	return stre;
}
