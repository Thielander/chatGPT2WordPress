#  code by Alexander Thiele 
#  https://www.linkedin.com/in/thielander/
#  alexander@thiele.es
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA#
#
import requests
import sys
import os
import re
import openai


from requests.auth import HTTPBasicAuth

# Clear screen
os.system('cls' if os.name == 'nt' else 'clear')

#OPENAI API KEY
openai.api_key = 'sk-YOUR-KEY'

##########WordPress config############
#WordPress url
wp_url = 'WPURL'

#WordPress user
wp_user = 'WPUSER'

#WordPress password
wp_password = 'WPPASS'

#Post type
wp_post_type = 'post'

#Categories (ids) single or separated by comma
wp_categories = '1,4'

#Status publish, future, draft, pending, private
wp_status = 'draft'

#Allow comments? open or closed
wp_comments = 'closed'

#Pings erlauben open oder closed
wp_ping = 'closed'

#Whether the post should be treated as sticky or not.
wp_sticky = True

#Tags or keywords
wp_tags = '5,6,7'

#Author
#wp_author = ''

##########WordPress config end############
if 'sk-YOUR-KEY' in openai.api_key:
    print("Please replace 'sk-YOUR-KEY' with your actual API key.")
    sys.exit()
    
if 'WPUSER' in wp_user:
    print("Please replace 'WPUSER' with your WordPress user.")
    sys.exit()

if 'WPPASS' in wp_password:
    print("Please replace 'WPPASS' with your WordPress password.")
    sys.exit()

if 'WPURL' in wp_url:
    print("Please replace 'WPUSER' with your WordPress URL.")
    sys.exit()

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    responsegpt = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return responsegpt.choices[0].message["content"]

prompt = f"""
Aufgabe:        "Erstelle mir einen Blogbeitrag Artikel über Digitalisierung."
Sprache:        "Deutsch"
Form:           "Du Form"
Sprachstil:     "locker, sachlich"
Länge:          "min. 2000 Wörter"
Aufbau:         "Einleitung, Haupteil , FAQ Sektion, Fazit"
Ziel:           "Neugierig machen auf meinen Content, Follower generieren" 
Den Titel bitte so <h2>Titel</h2> ausgeben
Überschriften bitte so <h3>Überschrift</h3> ausgeben.
Bitte den Text in <p>Text</p> ausgeben.
"""

englishprompt = f"""
Task: "Create me a blog post article about digitalization."
Language: "English"
Language style: "loose, factual"
Length: "min. 2000 words"
Structure: "introduction, main part , FAQ section, conclusion".
Goal: "make people curious about my content, generate followers". 
Please output the title like this <h2>Title</h2>.
Headings please output like this <h3>heading</h3>.
Please output the text in <p>text</p>.
"""

responsegpt = get_completion(prompt)

#Cut title
def extract_title(content):
    # Search for the content inside the <h2> tags
    match = re.search('<h2>(.*?)</h2>', content)
    if match:
        title = match.group(1)
        # Removes the title from the original content
        content = content.replace(match.group(0), '')
    else:
        title = ''
        
    return title, content

#Format output for Gutenberg
def format_content(content):
    content = content.replace("<h2>", "<!-- wp:heading {\"level\":2} -->\n<h2 class=\"wp-block-heading\">")
    content = content.replace("</h2>", "</h2>\n<!-- /wp:heading -->")

    content = content.replace("<h3>", "<!-- wp:heading {\"level\":3} -->\n<h3 class=\"wp-block-heading\">")
    content = content.replace("</h3>", "</h3>\n<!-- /wp:heading -->")

    content = content.replace("<h4>", "<!-- wp:heading {\"level\":4} -->\n<h4 class=\"wp-block-heading\">")
    content = content.replace("</h4>", "</h4>\n<!-- /wp:heading -->")

    content = content.replace("<h5>", "<!-- wp:heading{\"level\":5} -->\n<h5 class=\"wp-block-heading\">")
    content = content.replace("</h5>", "</h5>\n<!-- /wp:heading -->")

    content = content.replace("<p>", "<!-- wp:paragraph -->\n<p>")
    content = content.replace("</p>", "</p>\n<!-- /wp:paragraph -->")

    return content

#cut title
title, responsegpt = extract_title(responsegpt)

#Format text for Gutenberg
formatted_content = format_content(responsegpt)

def create_post(site_url, username, password, title, type, sticky, tags, comment_status, ping_status, categories, content, status):
    api_url = f"{site_url}/wp-json/wp/v2/posts"

    headers = {
        'Content-Type': 'application/json',
    }

    post = {
        'title': title,
        'type': type,
        'sticky': sticky,
        'tags' : tags,
        'comment_status': comment_status,
        'ping_status': ping_status,
        'categories': categories,
        'content': content,
        'status': status
    }

    response = requests.post(api_url, headers=headers, json=post, auth=HTTPBasicAuth(username, password))

    if response.status_code == 201:
        print("Post created successfully.")
    else:
        print(f"Error when creating the post: {response.content}")



create_post(wp_url, 
            wp_user, wp_password, 
            title,
            wp_post_type,
            wp_sticky,
            wp_tags,
            wp_comments,
            wp_ping,
            wp_categories, 
            formatted_content, 
            wp_status)
