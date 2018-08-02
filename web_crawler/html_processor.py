from bs4 import BeautifulSoup as bs

def extract_text(html): # actually not used in the project but might come in handy later so not deleted

    text = delete_comments(html)
    text = text.split('<body')[1]
    text = text[text.find('>')+1:]

    # delete text from <script to </script>
    script_start = 0
    while script_start != -1:
        script_start = text.find('<script')
        script_end = text.find('</script>') + 9
        text = text[:script_start] + text[script_end:]

    # delete text from <style to </style>
    style_start = 0
    while style_start != -1:
        style_start = text.find('<style')
        style_end = text.find('</style>') + 8
        text = text[:style_start] + text[style_end:]

    text = bs(text)
    
    text = text.get_text(separator = '\n')
    text = str(text)
    while text.find('\n\n') != -1:
        text = text.replace('\n\n', '\n') 

    return str(text)


def get_domain_name(url):  # gets domain name from url
    # based purely on string operations
    domain_name = url.split('://')[1]
    domain_name = domain_name.split('/')[0]
    if 'www' in domain_name:
        domain_name = domain_name.replace('www.', '')
    
    return domain_name


def delete_comments(html):
    commentless_html = html
    comment_start = 0
    a = 0
    while comment_start != -1:
        comment_start = commentless_html.find('<!--')
        comment_end = commentless_html.find('-->') + 3

        if comment_start == -1: # if did not find any
            break

        commentless_html = commentless_html[:comment_start] + commentless_html[comment_end:]
        a += 1

    while commentless_html.find('\n\n') != -1:  # get rid of double new lines
        commentless_html = commentless_html.replace('\n\n', '\n')

    return commentless_html

def html_comment(comm):
    return '<!--' + comm + '-->'

def extract_html_comment(comm):
    new_comm = comm.replace('<!--', '')
    new_comm = new_comm.replace('-->', '')
    new_comm = new_comm.replace('\n', '')
    new_comm = new_comm.replace('\t', '')
    return new_comm


