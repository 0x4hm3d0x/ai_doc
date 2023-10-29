#  6379142019:AAF1mviipa8wo2RQ-FnwUCMQhMb-Lp5EbEM"
import time
import textwrap
import openai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import telebot
from telebot import types
import os


api_key = os.getenv('OPENAI_API_KEY')

# Set up your OpenAI API key
openai.api_key = api_key

# Set up your OpenAI API key
#openai.api_key = ''

# Initialize the Telegram Bot
bot = telebot.TeleBot("6379142019:AAF1mviipa8wo2RQ-FnwUCMQhMb-Lp5EbEM")

# Function to generate text from GPT-3.5-turbo
def generate_text(prompt):
    messages = [
        {"role": "system", "content": "You are a creative writer."},
        {"role": "user", "content": prompt}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1000,
        temperature=1,
        top_p=0.5,
        frequency_penalty=0.5,
        presence_penalty=0.0
    )
    return response.choices[0].message["content"]
# Function to create a book
def create_book(user_input, message):
    num_chapters = 4  # Default value
    language = "en"  # Default language

    # Parse user options for number of chapters and language
    if "-nc" in user_input:
        options = user_input.split()
        index = options.index("-nc")
        if index + 1 < len(options):
            try:
                num_chapters = int(options[index + 1])
                user_input = ' '.join(options[:index] + options[index + 2:]).strip()
            except ValueError:
                pass

    if "-lng" in user_input:
        options = user_input.split()
        index = options.index("-lng")
        if index + 1 < len(options):
            language = options[index + 1]
            user_input = ' '.join(options[:index] + options[index + 2:]).strip()

    # Generate book title
    book_title = generate_text(f"Generate a title of a book about {user_input} in language {language}")
    bot.send_message(message.chat.id, "Book Title:\n" + book_title)  # Show title to user

    # Generate table of contents
    table_of_contents = generate_text(f"Generate {num_chapters} chapter titles for a book about {user_input} in language {language}")
    bot.send_message(message.chat.id, "Table of Contents:\n" + table_of_contents)  # Show contents to user

    table_of_contents_lines = table_of_contents.strip().split('\n')

    # Generate summary
    summary = generate_text(f"Write a short summary of a book about {user_input}. The title of the book is {book_title} in language {language}")

    # Generate book content
    book_content = []
    for chapter_line in table_of_contents_lines:
        chapter_title = chapter_line.strip()
        bot.send_message(message.chat.id, f"Generating content for chapter: {chapter_title}")
        chapter_content = generate_text(f"Write the content of {chapter_title} in the book about {user_input}. The title is {book_title} in language {language}")
        book_content.append(chapter_content)

    # Create the book content as a single string
    full_book_content = '\n\n'.join(book_content)

    return book_title, full_book_content


# Function to save text to a PDF using ReportLab with proper line breaks
def save_to_pdf(title, text, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(100, 750, title)

    text_paragraphs = text.split('\n\n')
    y_position = 700
    first_page = True
    for paragraph in text_paragraphs:
        lines = paragraph.split('\n')
        for line in lines:
            line_length = 80
            wrapped_lines = textwrap.wrap(line, line_length)
            for wrapped_line in wrapped_lines:
                c.drawString(100, y_position, wrapped_line)
                y_position -= 12
                if y_position < 50:
                    if first_page:
                        first_page = False
                    c.showPage()
                    y_position = 700
    c.showPage()
    c.save()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the Book Generator Bot! Please use /book followed by your request.")

@bot.message_handler(commands=['book'])
def generate_book(message):
    msg = bot.send_message(message.chat.id, "Please provide your request after /book, e.g., '/book story for kids'.")
    bot.register_next_step_handler(msg, process_book_request)

def process_book_request(message):
    user_input = message.text
    book_title, full_book_content = create_book(user_input, message)  # Pass the 'message' parameter

    # PDF and text file generation
    pdf_filename = "generated_book.pdf"
    text_filename = "generated_book.txt"
    save_to_pdf(book_title, full_book_content, pdf_filename)

    with open(text_filename, 'w', encoding='utf-8') as text_file:
        text_file.write(full_book_content)

    bot.send_message(message.chat.id, "Here's your generated book:")
    bot.send_document(message.chat.id, open(pdf_filename, 'rb'), caption="Generated PDF")
    bot.send_document(message.chat.id, open(text_filename, 'rb'), caption="Generated Text")


if __name__ == "__main__":
   bot.polling(none_stop=True, interval=5, timeout=60)
   bot.polling()
