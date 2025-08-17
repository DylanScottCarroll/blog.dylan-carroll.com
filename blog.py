import pypandoc
import json
import os
import re
import shutil
import sys
from datetime import datetime


class Post:
    def __init__(self, dir):
        self.id = dir.split("/")[-1]
        self.dir = dir
        data_dir = os.path.join(dir, "data.json")        
        body_dir = os.path.join(dir, "body.html")

        with open(data_dir) as f:
            data_dict = json.load(f)
            self.title = data_dict["title"]
            self.subtitle = data_dict["subtitle"]
            self.date = data_dict["date"]
            self.tags = data_dict["tags"]
        
        self.body = self.fetch_body(body_dir)

    def fetch_body(self, post_dir):
        extension = post_dir.split(".")[-1]
        with open(post_dir) as f:
            file_text = f.read()
        
        if extension == "md":
            return pypandoc.convert_text(file_text, 'html', format='gfm')
        
        elif extension=="html":
            return file_text

        else:
            raise ValueError("File type doesn't match :(")

    def format_metadata(self):
        return f"{self.date}" + (" | " if len(self.tags) > 0 else "") + ", ".join(self.tags) 


    def fill_template(self, template):
        template = re.sub(r"<!--\s*{post-title}\s*-->", self.title, template)
        if self.subtitle is not None:
            template = re.sub(r"<!--\s*{post-subtitle}\s*-->", self.subtitle, template)
        template = re.sub(r"<!--\s*{post-metadata}\s*-->", self.format_metadata(), template)
        template = re.sub(r"<!--\s*{post-body}\s*-->", self.body, template)
        template = re.sub(r"<!--\s*{post-url}\s*-->", self.id, template)
        return template


def refresh_dest_dir():
    shutil.rmtree("docs",)
    os.mkdir("docs")

    shutil.copytree("src/style", "docs/style")
    shutil.copytree("src/resources", "docs/resources")



def compile_blank_page(main_page=False):
    if main_page:
        with open("src/main-page-template.html") as f:
            page_template = f.read()
    else:
        with open("src/page-template.html") as f:
            page_template = f.read()
    
    with open("src/nav-header.html") as f:
        nav_header = f.read()

    with open("src/nav-aside.html") as f:
        nav_aside = f.read()

    page_template = re.sub(r"<!--\s*{nav-header}\s*-->", nav_header, page_template)
    page_template = re.sub(r"<!--\s*{nav-aside}\s*-->", nav_aside, page_template)

    return page_template



def compile_post(post, blank_page=None):
    # Load templates and fill in post
    if blank_page is None:
        blank_page = compile_blank_page()
    
    with open("src/post-template.html") as f:
        post_template = f.read()

    post_text = post.fill_template(post_template)
    post_page = re.sub(r"<!--\s*{main-contents}\s*-->", post_text, blank_page)


    shutil.copytree(
        os.path.join(post.dir, "resources", post.id),
        os.path.join("docs/resources/", post.id)
    )

    with open(os.path.join("docs", f"{post.id}.html"), "w") as f:
        f.write(post_page)


def compile_index(post_links):
    blank_page = compile_blank_page(main_page=True)
    post_page = re.sub(
        r"<!--\s*{main-contents}\s*-->",
        "".join(post_links),
        blank_page
    )

    with open("docs/index.html", "w") as f:
        f.write(post_page)

def compile_all():
    refresh_dest_dir()

    with open("src/post-link-template.html") as f:
        post_link_template = f.read()


    post_links = []

    posts = os.listdir("./content")
    for post in posts:
        dir = os.path.join("content/", post)
        post = Post(dir)

        post_links.append(post.fill_template(post_link_template))
            
        compile_post(post)

    compile_index(post_links)

def new_post():
    post_id = input("Post ID: ")
    os.mkdir(f"content/{post_id}")
    os.mkdir(f"content/{post_id}/resources/")
    os.mkdir(f"content/{post_id}/resources/{post_id}")
    data = ('{\n'
           f'\t"title": "{post_id}",\n'
           f'\t"subtitle": "",\n'
           f'\t"date" : "{datetime.now().strftime("%B %d, %y")}",\n'
           f'\t"tags" : []\n' 
           "}"
        )
    
    with open(f"content/{post_id}/data.json", "w") as f:
        f.write(data)

def usage():
    print("python compile.py compile|new")
    exit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage()
    elif "-h" in sys.argv[1]:
        usage()
    elif sys.argv[1] == "compile":
        compile_all()
    elif sys.argv[1] =="new":
        new_post()
    else:
        usage()

