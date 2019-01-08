from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib2 import urlopen
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def tag_visible(element):
    """
    only consider the tags listed in the dictionary
    :param element:
    :return:
    """
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(in_url):
    """
    Get the text from url
    :param in_url:
    :return:
    """
    body = urlopen('file://'+ in_url).read()
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    text = u" ".join(t.strip() for t in visible_texts)
    file_name = in_url.split('/')[-1]
    try:
        with open(file_name, 'w') as out_file:
            out_file.write(text)
            out_file.close()
    except:
        return False
    return True


if __name__ == "__main__":
    in_url = "/home/shahid/projects/behaviouralClassifier/DATA/18ccedfd35c7ec0bdbefca38fd2209da/url//page.html"
    text_from_html(in_url)
