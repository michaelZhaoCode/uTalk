from flask import Flask, request, jsonify, session
from flask_session import Session
from sql import load_messages, insert_message
from tempfile import mkdtemp
from api import reply
from dotenv import load_dotenv
load_dotenv()
import os
import openai
from sum_img import summarize
from time import sleep
from flask_cors import CORS, cross_origin
# openai.api_key = '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'
openai.api_key = os.environ.get('open_ai_key')

app = Flask(__name__)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
cors = CORS(app)
app.config['CONFIG_HEADERS'] = 'Content-Type'
TEXT = ['']
@app.route('/login/', methods=['POST'])
def login():
    session.clear()
    session['text'] = ''
    session['naive'] = "No"
    # hardcoding
    session['responses'] = ''
    # session['responses'] = [
    #     # i'm feeling pretty down
    #     "I'm sorry to hear that. Is there anything in particular that's been bothering you or anything I can do to help?",
    #     # i want to talk to someone
    #     "That's understandable. Are there any friends or family members you feel comfortable talking to? If not, there are also professional resources such as therapists or hotlines that you can reach out to for support.",
    #     # I have a friend named Michael, but he might be busy right now
    #     "If you're not sure if your friend Michael is available, you could try reaching out to him and asking if he has some time to talk.",
    #     # what do you think about my friend
    #     "I do not possess a particular opinion about individuals I do not know about, including your friend Michael. However, it's important to have a support system of friends and loved ones to talk to when you're feeling down. If you need additional support, you can consider reaching out to a therapist or counselor.",
    #     # did you know I like black forest cake
    #     "I do not have the ability to know or remember information about you unless you have provided that information to me before. However, I can tell you that Black Forest Cake is a traditional German chocolate cake that usually layers chocolate cake, whipped cream and cherries. It is a delicious and popular cake enjoyed by many people around the world.",
    #     # do you think my friend will like it as well
    #     "I don't have the ability to know or predict if your friend Michael will like Black Forest Cake or any other food. Taste preferences can vary widely from person to person and depend on many factors. It would be best to ask your friend directly or offer them a slice and see what they think."
    # ]

    email = request.get_json()['email']
    session['email'] = email
    print(session['email'])

    response = {
        # Add this option to distinct the POST request
        'email': email,
        "METHOD": "POST"
    }
    return jsonify(response)


@app.route('/messagetype/', methods=['POST'])
def messagetype():
    naive = request.get_json()['naive']
    session['naive'] = naive
    response = {
        # Add this option to distinct the POST request
        'naive': naive,
        "METHOD": "POST"
    }
    return jsonify(response)


@app.route('/message/', methods=['POST'])
def message():

    email = 'varun@email.com'
    input_message = request.get_json()['message']
    big_string = ''
    if session.get('text') is None:
        session['text'] = ""


    user_data = load_messages(email)

    for i in range(len(user_data)):
        cur_tuple = user_data[i]
        big_string += cur_tuple[0]
        big_string += '\n--\n'

    big_string += f'Input:{input_message}\nResponse:'

    response = reply(big_string).replace('Thank you for your response!', '').replace("\n", "").replace('--', '').strip()

    new_message = f'Input: {input_message}\nResponse:{response}'
    TEXT[0] += new_message + '\n'

    insert_message(email, new_message)


    new_response = {
        # Add this option to distinct the POST request
        'response': response
    }
    return jsonify(new_response)


@app.route('/image/', methods=['GET'])
def image():
    new_text = TEXT[0].replace('--', '').replace('Input: ', '').replace('Response:', '')
    new_text += f'\n\nSummary:'
    # print("*********", text, "*********")
    prompt = summarize(new_text)
    
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    return jsonify(image_url)



if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)


{"message": "I want to make friends. Please help"}
{"message": "I am so lonely"}
{"email": "varun@email.com"}
{"naive": "No"}
