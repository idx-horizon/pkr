import re
import bs4

def get_chunk_as_tuples(datalist, n):
    """Yield successive n-sized chunks as tuple from datalist"""
    for i in range(0, len(datalist), n):
        yield tuple(datalist[i:i + n])

def get_run_links(pagetext):
	soup = bs4.BeautifulSoup(pagetext,'html5lib')
	y = soup.find_all('table')[2]
	ass = y.find_all('a')
	links = []
	for link in set([x for x in ass if 'runSeqNumber' in x.get('href')]): 
		href = link.get('href').split('/')[2]
		if href not in links:
			links.append(href)
	
	return links


def extract_tables(html_text):
	table_pattern = r'(<table[^>]*>(?:.|\n)*?<\/table>)' 
	header_pattern = r'(<th[^e/]*>(?:.|\n)*?<\/th>)'
	caption_pattern = r'<caption>*>(?:.|\n)*?<\/caption>'
	td_pattern = r'<td>*>(?:.|\n)*?<\/td>'
	h2_pattern = r'<h2>*>(?:.|\n)*?<\/h2>'
	remove_tag_pattern = r'<[^>]*>'

	tables = re.findall(table_pattern, html_text)
	response = {}
	table_count = 0
	
	h2 = re.findall(h2_pattern, html_text)
	if h2:
		h2name = re.sub(remove_tag_pattern,'', h2[0].replace('<br/>',' ')).replace('\n',' ')
	else:
		h2name = 'Unknown'
	
	for t in tables[0:3]:
		table_count += 1
		captions = re.findall(caption_pattern,t)
		if captions:
			caption = re.sub(remove_tag_pattern,'', captions[0])
		else:
			caption = str(table_count) + '. Table'
			
		headers = [re.sub(remove_tag_pattern,'',h) for h in re.findall(header_pattern, t)]
		for e in re.findall(r'<th\/>', t):
			headers.insert(0,'')
			
		i = 1
		data = [re.sub(remove_tag_pattern,'',d).strip() for d in re.findall(td_pattern,t)]

		runs =[]
		for i in get_chunk_as_tuples(data,len(headers)):
			runs.append(i)

		run_list = [{k: v for k, v in zip(headers, tup)} for tup in list(runs)]

		response[table_count] = {'headers': headers,
									'number_cols': len(headers),
#									'data_count': len(data),
									'data': data,
									'runs': run_list,
									'caption': caption.strip(),
									'title': h2name.strip()}
	return response