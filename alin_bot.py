## Antes de começar, executar no Shell: 
## pip install python-telegram-bot
import Bio
from Bio import SeqIO
from Bio import pairwise2
from Bio import AlignIO
import telegram
import telegram.ext 
import logging
import re
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# The API Key we received for our bot
API_KEY = ""
# Create an updater object with our API Key
updater = telegram.ext.Updater(API_KEY, use_context=True)
# Retrieve the dispatcher, which will be used to add handlers
dispatcher = updater.dispatcher

WELCOME = 0
FILE = 1
CANCEL = 2
CORRECT = 3

def start(update_obj, context):
    # Call to align sequences
    update_obj.message.reply_text("Hello there, do you want to align some sequences? (Yes/No)",
        reply_markup=telegram.ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True)
    )
    # go to the WELCOME state
    return WELCOME


# in the WELCOME state, check if the user wants to answer a question
def welcome(update_obj, context):
    if update_obj.message.text.lower() in ['yes', 'y']:
        # send question, and go to the QUESTION state
      update_obj.message.reply_text("send the fasta files of the sequences you want to align")
      return FILE
    else:
      # go to the CANCEL state
      update_obj.message.reply_text("cancel")
      first_name = update_obj.message.from_user['first_name']
      update_obj.message.reply_text(
          f"Okay, no alignment for you then, take care, {first_name}!", reply_markup=telegram.ReplyKeyboardRemove()
      )
      return telegram.ext.ConversationHandler.END
      #return CANCEL

# in the QUESTION state
def file(update_obj, context):
      # writing to a custom file
    nome_do_arq = update_obj.message.document.file_id
    arquivo = context.bot.get_file(update_obj.message.document)
    arquivo.download(custom_path="./arquivo.txt")
    update_obj.message.reply_text("Thanks for the file " + nome_do_arq)
    #    alinhar aqui
    x = []
    for record in SeqIO.parse("arquivo.txt", "fasta"):
      x.append(record.seq)
      print(record.id)
    alignments = pairwise2.align.globalxx(x[0], x[1])

    update_obj.message.reply_text("Here is your result:")
    # ENVIAR ARQUIVO DO ALINHAMENTO
    #SeqIO.write(alignments[0], "artemis_out.txt", "fasta")
    update_obj.message.reply_text(alignments)
    with open("artemis_out.txt", "w") as file:
      for al in alignments:
        file.write(pairwise2.format_alignment(*al))
    # enviar
    update_obj.send_document("artemis_out.txt")
    # get the user's first name
    first_name = update_obj.message.from_user['first_name']
    update_obj.message.reply_text(f"See you {first_name}!, bye")
    return telegram.ext.ConversationHandler.END

# in the CORRECT state
#def correct(update_obj, context):
 #   update_obj.message.reply_text("Here is your result:")
    # ENVIAR ARQUIVO DO ALINHAMENTO
    
    # get the user's first name
  #  first_name = update_obj.message.from_user['first_name']
   # update_obj.message.reply_text(f"See you {first_name}!, bye")
   # return telegram.ext.ConversationHandler.END


def cancel(update_obj, context): 
    # get the user's first name
    first_name = update_obj.message.from_user['first_name']
    update_obj.message.reply_text(
        f"Okay, no alignment for you then, take care, {first_name}!", reply_markup=telegram.ReplyKeyboardRemove()
    )
    return telegram.ext.ConversationHandler.END


#####
# a regular expression that matches yes or no
yes_no_regex = re.compile(r'^(yes|no|y|n)$', re.IGNORECASE)
cancel_regex = re.compile(r'^(cancel|c)$', re.IGNORECASE)
# Create our ConversationHandler, with only four states
handler = telegram.ext.ConversationHandler(
      entry_points=[telegram.ext.CommandHandler('start', start)],
      states={
            WELCOME: [telegram.ext.MessageHandler(telegram.ext.Filters.regex(yes_no_regex), welcome)],
            FILE: [telegram.ext.MessageHandler(telegram.ext.filters.Filters.document.file_extension("txt"), file)],
            #CANCEL: [telegram.ext.MessageHandler(telegram.ext.Filters.regex(cancel_regex), cancel)]
            #CORRECT: [telegram.ext.MessageHandler(telegram.ext.Filters.regex(yes_no_regex), correct)],
            
      },
      fallbacks=[telegram.ext.MessageHandler(telegram.ext.Filters.regex(cancel_regex), cancel)],

      #telegram.ext.CommandHandler('cancel', cancel)],
      allow_reentry=False #tentar mexer no futuro
      )

#updater.dispatcher.add_handler(MessageHandler(Filters.document, downloader))
# add the handler to the dispatcher
dispatcher.add_handler(handler)
# start polling for updates from Telegram
updater.start_polling()
# block until a signal (like one sent by CTRL+C) is sent
updater.idle()


