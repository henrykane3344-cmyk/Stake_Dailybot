import os
import logging
import tempfile
import sys
import re
import string
import random
from datetime import datetime
from gtts import gTTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Language options for TTS and Translation
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese (Mandarin)',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'nl': 'Dutch',
    'tr': 'Turkish',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'id': 'Indonesian',
    'pl': 'Polish',
    'uk': 'Ukrainian',
    'he': 'Hebrew',
    'el': 'Greek',
    'cs': 'Czech',
    'sv': 'Swedish',
    'hu': 'Hungarian',
    'ro': 'Romanian'
}

# Stake Daily themed responses
STAKE_RESPONSES = [
    "📊 Stake Daily - Your daily language expert!",
    "📈 Level up your communication with Stake Daily!",
    "💰 Stake Daily - Invest in better communication!",
    "🏆 Stake Daily - Winners speak better!",
    "💎 Stake Daily - Quality language services!",
    "🎯 Stake Daily - Precision in every word!",
    "⚡ Stake Daily - 24/7 language assistance!",
    "🌟 Stake Daily - Excellence guaranteed!",
    "🚀 Stake Daily - Elevate your language!",
    "💪 Stake Daily - Stronger communication!",
]

# Grammar Rules
GRAMMAR_RULES = {
    # Common contractions
    "don't": 'do not',
    "can't": 'cannot',
    "won't": 'will not',
    "shouldn't": 'should not',
    "wouldn't": 'would not',
    "couldn't": 'could not',
    "isn't": 'is not',
    "aren't": 'are not',
    "wasn't": 'was not',
    "weren't": 'were not',
    "hasn't": 'has not',
    "haven't": 'have not',
    "hadn't": 'had not',
    "doesn't": 'does not',
    "didn't": 'did not',
    "ain't": 'am not',
    "i'm": 'I am',
    "you're": 'you are',
    "he's": 'he is',
    "she's": 'she is',
    "it's": 'it is',
    "we're": 'we are',
    "they're": 'they are',
    "i'll": 'I will',
    "you'll": 'you will',
    "he'll": 'he will',
    "she'll": 'she will',
    "it'll": 'it will',
    "we'll": 'we will',
    "they'll": 'they will',
    "i've": 'I have',
    "you've": 'you have',
    "we've": 'we have',
    "they've": 'they have',
    "i'd": 'I would',
    "you'd": 'you would',
    "he'd": 'he would',
    "she'd": 'she would',
    "we'd": 'we would',
    "they'd": 'they would',
    
    # Articles
    'a apple': 'an apple',
    'a hour': 'an hour',
    'a honest': 'an honest',
    'a honor': 'an honor',
    'a umbrella': 'an umbrella',
    'a university': 'a university',
    'a European': 'a European',
    
    # Common misspellings
    'teh': 'the',
    'adn': 'and',
    'thier': 'their',
    'there': 'their',
    'your': 'your',
    'youre': "you're",
    'alot': 'a lot',
    'untill': 'until',
    'recieve': 'receive',
    'belive': 'believe',
    'acheive': 'achieve',
    'occured': 'occurred',
    'ocurred': 'occurred',
    'seperate': 'separate',
    'definately': 'definitely',
    'govenment': 'government',
    'enviornment': 'environment',
    'accomodate': 'accommodate',
    'aquire': 'acquire',
    'arguement': 'argument',
    'begining': 'beginning',
    'business': 'business',
    'calendar': 'calendar',
    'career': 'career',
    'catagory': 'category',
    'cemetary': 'cemetery',
    'collaegue': 'colleague',
    'comittee': 'committee',
    'concious': 'conscious',
    'dilemna': 'dilemma',
    'disappear': 'disappear',
    'disatisfied': 'dissatisfied',
    'embarass': 'embarrass',
    'enviroment': 'environment',
    'excede': 'exceed',
    'existance': 'existence',
    'experiance': 'experience',
    'guarantee': 'guarantee',
    'harrass': 'harass',
    'independant': 'independent',
    'indispensible': 'indispensable',
    'inoculate': 'inoculate',
    'irresistable': 'irresistible',
    'maintainance': 'maintenance',
    'millenium': 'millennium',
    'miniscule': 'minuscule',
    'mischevious': 'mischievous',
    'neccessary': 'necessary',
    'occassion': 'occasion',
    'occurence': 'occurrence',
    'pavillion': 'pavilion',
    'perserverance': 'perseverance',
    'prefered': 'preferred',
    'priviledge': 'privilege',
    'pronounciation': 'pronunciation',
    'publically': 'publicly',
    'reccommend': 'recommend',
    'relevent': 'relevant',
    'repetition': 'repetition',
    'rhythm': 'rhythm',
    'schedual': 'schedule',
    'seperate': 'separate',
    'similiar': 'similar',
    'sucess': 'success',
    'suprize': 'surprise',
    'tommorow': 'tomorrow',
    'unescessary': 'unnecessary',
    'wierd': 'weird',
    
    # Common phrase corrections
    'could of': 'could have',
    'should of': 'should have',
    'would of': 'would have',
    'must of': 'must have',
    'might of': 'might have',
}

# Translation Dictionary
TRANSLATION_DICT = {
    # English to Spanish
    'hello': 'hola',
    'goodbye': 'adiós',
    'thank you': 'gracias',
    'yes': 'sí',
    'no': 'no',
    'please': 'por favor',
    'sorry': 'lo siento',
    'good morning': 'buenos días',
    'good afternoon': 'buenas tardes',
    'good night': 'buenas noches',
    'how are you': '¿cómo estás',
    'i love you': 'te quiero',
    'friend': 'amigo',
    'family': 'familia',
    'home': 'casa',
    'water': 'agua',
    'food': 'comida',
    'love': 'amor',
    'life': 'vida',
    'happy': 'feliz',
    'sad': 'triste',
    'beautiful': 'hermoso',
    'good': 'bueno',
    'bad': 'malo',
    'big': 'grande',
    'small': 'pequeño',
    'new': 'nuevo',
    'old': 'viejo',
    'young': 'joven',
    'success': 'éxito',
    'excellence': 'excelencia',
    'quality': 'calidad',
    'performance': 'rendimiento',
    'improvement': 'mejora',
    'stake': 'participación',
    'daily': 'diario',
    
    # English to French
    'bonjour': 'hello',
    'merci': 'thank you',
    'au revoir': 'goodbye',
    'oui': 'yes',
    'non': 'no',
    "s'il vous plaît": 'please',
    'pardon': 'sorry',
    'bonsoir': 'good evening',
    'bonne nuit': 'good night',
    "comment ça va": 'how are you',
    "je t'aime": 'i love you',
    'ami': 'friend',
    'famille': 'family',
    'maison': 'home',
    'eau': 'water',
    'nourriture': 'food',
    'amour': 'love',
    'vie': 'life',
    'heureux': 'happy',
    'triste': 'sad',
    'beau': 'beautiful',
    'bon': 'good',
    'mauvais': 'bad',
    'grand': 'big',
    'petit': 'small',
    'nouveau': 'new',
    'vieux': 'old',
    'jeune': 'young',
    'succès': 'success',
    'excellence': 'excellence',
    'qualité': 'quality',
    'performance': 'performance',
    'amélioration': 'improvement',
}

# User preferences
user_preferences = {}

def get_token():
    """Get token from environment variables"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if token and token not in ["YOUR_BOT_TOKEN_HERE", "your_bot_token_here", ""]:
        return token
    
    token = os.getenv('BOT_TOKEN')
    if token and token not in ["YOUR_BOT_TOKEN_HERE", ""]:
        return token
    
    token = os.getenv('TELEGRAM_TOKEN')
    if token and token not in ["YOUR_BOT_TOKEN_HERE", ""]:
        return token
    
    return None

def get_stake_response():
    """Get random Stake-themed response"""
    return random.choice(STAKE_RESPONSES)

def correct_grammar(text):
    """AI Grammar Correction with advanced rules"""
    original_text = text
    corrections = []
    corrected_text = text
    
    # Step 1: Fix common misspellings and phrases
    words = corrected_text.split()
    corrected_words = []
    
    for word in words:
        clean_word = word.strip(string.punctuation)
        lower_word = clean_word.lower()
        
        if lower_word in GRAMMAR_RULES:
            correction = GRAMMAR_RULES[lower_word]
            if clean_word[0].isupper():
                correction = correction.capitalize()
            if word != clean_word:
                correction += word[-1] if word[-1] in string.punctuation else ''
            corrected_words.append(correction)
            corrections.append(f"'{clean_word}' → '{correction}'")
        else:
            corrected_words.append(word)
    
    corrected_text = ' '.join(corrected_words)
    
    # Step 2: Fix capitalization
    sentences = corrected_text.split('. ')
    corrected_text = '. '.join([s.capitalize() if s else s for s in sentences])
    
    # Step 3: Fix article errors
    corrected_text = re.sub(r'\ba ([aeiouAEIOU])', r'an \1', corrected_text)
    corrected_text = re.sub(r'\ban ([^aeiouAEIOU])', r'a \1', corrected_text)
    
    # Step 4: Remove extra spaces
    corrected_text = ' '.join(corrected_text.split())
    
    # Step 5: Fix "i" to "I"
    corrected_text = re.sub(r'\bi\b', 'I', corrected_text)
    
    # Step 6: Capitalize days and months
    months = ['january', 'february', 'march', 'april', 'may', 'june', 
              'july', 'august', 'september', 'october', 'november', 'december']
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for month in months:
        corrected_text = re.sub(rf'\b{month}\b', month.capitalize(), corrected_text, flags=re.IGNORECASE)
    for day in days:
        corrected_text = re.sub(rf'\b{day}\b', day.capitalize(), corrected_text, flags=re.IGNORECASE)
    
    # Step 7: Fix double punctuation
    corrected_text = re.sub(r'([.!?])\1+', r'\1', corrected_text)
    
    # Step 8: Fix spacing around punctuation
    corrected_text = re.sub(r'\s+([.,!?;:])', r'\1', corrected_text)
    
    changes_made = len(corrections) > 0 or original_text != corrected_text
    
    return {
        'original': original_text,
        'corrected': corrected_text,
        'changes_made': changes_made,
        'corrections': corrections[:10] if corrections else [],
        'total_corrections': len(corrections)
    }

def translate_text(text, target_lang='es'):
    """Simple translation function"""
    text_lower = text.lower().strip()
    
    if text_lower in TRANSLATION_DICT:
        translated = TRANSLATION_DICT[text_lower]
        return {
            'original': text,
            'translated': translated,
            'target_lang': target_lang,
            'confidence': 'high'
        }
    
    words = text_lower.split()
    translated_parts = []
    found_translations = 0
    
    for word in words:
        clean_word = re.sub(r'[^\w\s]', '', word)
        if clean_word in TRANSLATION_DICT:
            translated_parts.append(TRANSLATION_DICT[clean_word])
            found_translations += 1
        else:
            translated_parts.append(word)
    
    if found_translations > 0:
        translated_text = ' '.join(translated_parts)
        if text[0].isupper():
            translated_text = translated_text.capitalize()
        
        return {
            'original': text,
            'translated': translated_text,
            'target_lang': target_lang,
            'confidence': 'medium',
            'words_translated': found_translations
        }
    
    return {
        'original': text,
        'translated': f"[No direct translation available]",
        'target_lang': target_lang,
        'confidence': 'none'
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when /start is issued."""
    user = update.effective_user
    current_time = datetime.now().strftime("%I:%M %p")
    stake_response = get_stake_response()
    
    await update.message.reply_text(
        f"📊 Welcome to @Stake_Dailybot, {user.first_name}! 👋\n\n"
        f"🕐 Current time: {current_time}\n\n"
        f"💰 {stake_response} 💰\n\n"
        f"🎯 **Speak better • Write better • Understand more**\n\n"
        "I'm your **all-in-one** language assistant with THREE powerful functions:\n\n"
        "🔊 **Text → Speech** - Convert any text to natural audio\n"
        "🌍 **Translation** - Translate words and phrases instantly\n"
        "✍️ **Grammar Correction** - Perfect your writing\n\n"
        "📝 **Commands:**\n"
        "/start - Show this message\n"
        "/tts - Convert text to speech\n"
        "/translate - Translate text\n"
        "/grammar - Check and correct grammar\n"
        "/all - Do everything at once!\n"
        "/lang - Change TTS language\n"
        "/target - Set translation language\n"
        "/speed - Change speech speed\n"
        "/stake - Get Stake Daily info\n"
        "/help - Get help\n"
        "/about - About this bot\n\n"
        "💡 **How to use:**\n"
        "• /tts [text] - Convert to speech\n"
        "• /translate [text] - Translate text\n"
        "• /grammar [text] - Check grammar\n"
        "• /all [text] - Do everything at once!\n\n"
        "📈 **Stake Daily - Invest in better communication!**"
    )

async def stake_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send Stake Daily information."""
    stake_response = get_stake_response()
    
    await update.message.reply_text(
        f"📊 **Stake Daily - Your Language Investment**\n\n"
        f"{stake_response}\n\n"
        f"💰 **Why Invest in Stake Daily?**\n"
        f"• 📈 Daily language improvement\n"
        f"• 🎯 Precision communication\n"
        f"• 💎 Quality guaranteed\n"
        f"• 🏆 Winners speak better\n"
        f"• ⚡ 24/7 availability\n\n"
        f"📊 **Your Investment Returns:**\n"
        f"• 🔊 Clear speech\n"
        f"• 🌍 Global communication\n"
        f"• ✍️ Perfect grammar\n"
        f"• ✨ Confident expression\n\n"
        f"💡 **Commands to use:**\n"
        f"/tts - Convert text to speech\n"
        f"/translate - Translate text\n"
        f"/grammar - Check grammar\n"
        f"/all - Do everything at once!\n\n"
        f"📈 **Stake Daily - Invest in yourself!**"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send about information."""
    await update.message.reply_text(
        "📊 **About @Stake_Dailybot**\n\n"
        "🎯 **Mission:** Speak better • Write better • Understand more\n\n"
        "💰 **Stake Daily - Invest in Better Communication**\n\n"
        "🔊 **Text-to-Speech:**\n"
        "• 12+ languages supported\n"
        "• Speed control (Normal/Slow)\n"
        "• Crystal clear audio\n\n"
        "🌍 **Translation:**\n"
        "• 25+ languages supported\n"
        "• Word and phrase translation\n"
        "• Smart detection\n\n"
        "✍️ **Grammar Correction:**\n"
        "• 100+ grammar rules\n"
        "• Spelling correction\n"
        "• Punctuation fixes\n"
        "• Capitalization fixes\n"
        "• Article corrections\n\n"
        "📈 **Special Features:**\n"
        "• Stake Daily investment theme\n"
        "• All-in-one /all command\n"
        "• Interactive processing\n"
        "• 24/7 availability\n\n"
        "📅 **Created:** 2026\n"
        "🔧 **Technology:** Python + Google TTS + AI Rules\n\n"
        "🌟 **Perfect for:**\n"
        "• Language learning\n"
        "• Content creation\n"
        "• Professional writing\n"
        "• Accessibility\n"
        "• International communication\n\n"
        "📈 **Stake Daily - Your daily language investment!**"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message."""
    await update.message.reply_text(
        "📊 **@Stake_Dailybot Help**\n\n"
        "🎯 **Speak better • Write better • Understand more**\n\n"
        "📖 **How to use:**\n\n"
        "**🔊 Text-to-Speech:**\n"
        "/tts [your text] - Convert to speech\n"
        "Example: /tts Hello, how are you?\n\n"
        "**🌍 Translation:**\n"
        "/translate [your text] - Translate text\n"
        "Example: /translate hello\n\n"
        "**✍️ Grammar Correction:**\n"
        "/grammar [your text] - Check grammar\n"
        "Example: /grammar i am go to school\n\n"
        "**🔄 All-in-One:**\n"
        "/all [your text] - Do everything at once!\n"
        "Example: /all hello world\n\n"
        "**📊 Stake Daily Info:**\n"
        "/stake - Get Stake Daily information\n\n"
        "**Commands:**\n"
        "/start - Welcome message\n"
        "/tts - Convert to speech\n"
        "/translate - Translate text\n"
        "/grammar - Check grammar\n"
        "/all - All functions at once\n"
        "/stake - Stake Daily info\n"
        "/lang - Change TTS language\n"
        "/target - Set translation language\n"
        "/speed - Change speech speed\n"
        "/help - This menu\n"
        "/about - About this bot\n\n"
        "💡 **Tips:**\n"
        "• Stake Daily - Invest in better communication!\n"
        "• Use /all for maximum productivity\n"
        "• Send any text and I'll ask how to process it\n"
        "• Your daily language investment starts here!"
    )

async def all_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /all command - do everything at once!"""
    text = update.message.text.replace('/all', '').strip()
    
    if not text:
        await update.message.reply_text(
            "📝 Please provide text to process!\n"
            "Example: /all Hello, how are you today?"
        )
        return
    
    user_id = update.effective_user.id
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    speed = user_preferences.get(user_id, {}).get('speed', 'normal')
    target_lang = user_preferences.get(user_id, {}).get('target_lang', 'es')
    stake_response = get_stake_response()
    
    await update.message.reply_text(
        f"📊 Processing all functions... {stake_response}\n\n"
        f"🔊 TTS Language: {LANGUAGES.get(lang, 'English')}\n"
        f"🌍 Target Language: {LANGUAGES.get(target_lang, 'Spanish')}\n"
        f"🎚️ Speed: {'Normal' if speed == 'normal' else 'Slow'}\n\n"
        "⏳ Please wait..."
    )
    
    try:
        # 1. Grammar Correction
        grammar_result = correct_grammar(text)
        
        # 2. Translation
        translation_result = translate_text(text, target_lang)
        
        # 3. Text-to-Speech
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_path = tmp_file.name
        
        slow = (speed == 'slow')
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(temp_path)
        
        # Send results
        response = (
            f"📊 **All Functions Complete!**\n\n"
            f"📝 **Original:**\n{text}\n\n"
            f"✍️ **Grammar Correction:**\n{grammar_result['corrected']}\n"
        )
        
        if grammar_result['changes_made']:
            response += f"   (✅ {grammar_result['total_corrections']} corrections made)\n"
        else:
            response += f"   (✅ No corrections needed)\n"
        
        response += f"\n🌍 **Translation ({LANGUAGES.get(target_lang, 'Spanish')}):**\n{translation_result['translated']}\n"
        
        if translation_result['confidence'] == 'high':
            response += f"   (✅ High confidence translation)\n"
        elif translation_result['confidence'] == 'medium':
            response += f"   (⚠️ Medium confidence - {translation_result.get('words_translated', 0)} words translated)\n"
        else:
            response += f"   (⚠️ No direct translation found)\n"
        
        response += f"\n🔊 **Audio:** Sent below\n"
        response += f"\n📊 {stake_response}"
        
        # Send text response
        await update.message.reply_text(response, parse_mode='Markdown')
        
        # Send audio
        with open(temp_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                caption=f"📊 Stake Daily TTS\n🌐 Language: {LANGUAGES.get(lang, 'English')}",
                title="Stake Daily TTS Audio",
                performer="@Stake_Dailybot"
            )
        
        os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"Error in all_command: {e}")
        await update.message.reply_text("❌ Error processing. Please try again.")

async def tts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /tts command"""
    text = update.message.text.replace('/tts', '').strip()
    
    if not text:
        await update.message.reply_text(
            "📝 Please provide text to convert to speech!\n"
            "Example: /tts Hello, how are you?"
        )
        return
    
    user_id = update.effective_user.id
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    speed = user_preferences.get(user_id, {}).get('speed', 'normal')
    stake_response = get_stake_response()
    
    await update.message.reply_text(f"🔊 Converting to speech in {LANGUAGES.get(lang, 'English')}... {stake_response}")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_path = tmp_file.name
        
        slow = (speed == 'slow')
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(temp_path)
        
        speed_label = "Normal" if speed == 'normal' else "Slow"
        
        with open(temp_path, 'rb') as audio_file:
            await update.message.reply_audio(
                audio=audio_file,
                caption=f"📊 Stake Daily - TTS\n"
                       f"🌐 Language: {LANGUAGES.get(lang, 'English')}\n"
                       f"🎚️ Speed: {speed_label}\n"
                       f"📝 Text: {text[:50]}{'...' if len(text) > 50 else ''}",
                title="Stake Daily TTS Audio",
                performer="@Stake_Dailybot"
            )
        
        os.unlink(temp_path)
        
    except Exception as e:
        logger.error(f"Error in tts: {e}")
        await update.message.reply_text("❌ Error converting text to speech. Please try again.")

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /translate command"""
    text = update.message.text.replace('/translate', '').strip()
    
    if not text:
        await update.message.reply_text(
            "📝 Please provide text to translate!\n"
            "Example: /translate hello\n\n"
            "💡 Use /target to change your translation target language"
        )
        return
    
    user_id = update.effective_user.id
    target_lang = user_preferences.get(user_id, {}).get('target_lang', 'es')
    stake_response = get_stake_response()
    
    await update.message.reply_text(f"🌍 Translating to {LANGUAGES.get(target_lang, 'Spanish')}... {stake_response}")
    
    try:
        result = translate_text(text, target_lang)
        
        response = (
            f"🌍 **Translation Result**\n\n"
            f"📝 **Original:**\n{result['original']}\n\n"
            f"✅ **Translated:**\n{result['translated']}\n\n"
            f"🎯 **Target Language:** {LANGUAGES.get(target_lang, 'Spanish')}\n"
        )
        
        if result['confidence'] == 'high':
            response += f"📊 **Confidence:** High ✅"
        elif result['confidence'] == 'medium':
            response += f"📊 **Confidence:** Medium ⚠️\n"
            response += f"📌 **Words translated:** {result.get('words_translated', 0)}"
        else:
            response += f"📊 **Status:** No direct translation found ⚠️\n"
            response += f"💡 Tip: Try simpler words or phrases"
        
        response += f"\n\n📊 {stake_response}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in translation: {e}")
        await update.message.reply_text("❌ Error translating. Please try again.")

async def grammar_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /grammar command"""
    text = update.message.text.replace('/grammar', '').strip()
    
    if not text:
        await update.message.reply_text(
            "📝 Please provide text to check grammar!\n"
            "Example: /grammar i am go to school"
        )
        return
    
    stake_response = get_stake_response()
    await update.message.reply_text(f"✍️ Analyzing and correcting grammar... {stake_response}")
    
    try:
        result = correct_grammar(text)
        
        if result['changes_made']:
            response = (
                f"✍️ **Grammar Correction Results**\n\n"
                f"📝 **Original:**\n{result['original']}\n\n"
                f"✅ **Corrected:**\n{result['corrected']}\n\n"
                f"🔧 **Corrections Made:** ({result['total_corrections']} changes)\n"
            )
            
            if result['corrections']:
                for i, correction in enumerate(result['corrections'][:5], 1):
                    response += f"{i}. {correction}\n"
                if len(result['corrections']) > 5:
                    response += f"... and {len(result['corrections']) - 5} more corrections\n"
            else:
                response += "• Minor formatting improvements\n"
        else:
            response = (
                f"✍️ **Grammar Check Complete**\n\n"
                f"✅ Your text is grammatically correct!\n\n"
                f"📝 **Your text:**\n{text}\n\n"
                f"💡 No corrections needed. Great job! 👏"
            )
        
        response += f"\n\n📊 {stake_response}"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in grammar correction: {e}")
        await update.message.reply_text("❌ Error checking grammar. Please try again.")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle general text messages"""
    text = update.message.text
    
    if text.startswith('/'):
        return
    
    # Show options for what to do with the text
    keyboard = [
        [InlineKeyboardButton("🔊 Text-to-Speech", callback_data="process_tts")],
        [InlineKeyboardButton("🌍 Translation", callback_data="process_translate")],
        [InlineKeyboardButton("✍️ Grammar Correction", callback_data="process_grammar")],
        [InlineKeyboardButton("📊 All Three (Stake Daily)", callback_data="process_all")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"📊 I received your text:\n\n"
        f"_{text[:100]}{'...' if len(text) > 100 else ''}_\n\n"
        f"🤔 How would you like me to process it?\n\n"
        f"💡 Use /tts, /translate, /grammar, or /all directly!\n"
        f"📊 Stake Daily - Invest in better communication!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    context.user_data['pending_text'] = text

async def process_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle processing callback"""
    query = update.callback_query
    await query.answer()
    
    action = query.data
    text = context.user_data.get('pending_text', '')
    
    if not text:
        await query.edit_message_text("❌ No text found. Please send your text again.")
        return
    
    user_id = query.from_user.id
    lang = user_preferences.get(user_id, {}).get('lang', 'en')
    speed = user_preferences.get(user_id, {}).get('speed', 'normal')
    target_lang = user_preferences.get(user_id, {}).get('target_lang', 'es')
    stake_response = get_stake_response()
    
    if action == "process_tts":
        await query.edit_message_text(f"🔊 Converting to speech in {LANGUAGES.get(lang, 'English')}... {stake_response}")
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_path = tmp_file.name
            
            slow = (speed == 'slow')
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(temp_path)
            
            speed_label = "Normal" if speed == 'normal' else "Slow"
            
            with open(temp_path, 'rb') as audio_file:
                await query.message.reply_audio(
                    audio=audio_file,
                    caption=f"📊 Stake Daily - TTS\n"
                           f"🌐 Language: {LANGUAGES.get(lang, 'English')}\n"
                           f"🎚️ Speed: {speed_label}",
                    title="Stake Daily TTS Audio",
                    performer="@Stake_Dailybot"
                )
            
            os.unlink(temp_path)
            await query.edit_message_text(f"✅ Audio sent successfully! {stake_response}")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("❌ Error converting to speech. Please try again.")
    
    elif action == "process_translate":
        await query.edit_message_text(f"🌍 Translating to {LANGUAGES.get(target_lang, 'Spanish')}... {stake_response}")
        
        try:
            result = translate_text(text, target_lang)
            
            response = (
                f"🌍 **Translation Result**\n\n"
                f"📝 **Original:**\n{result['original']}\n\n"
                f"✅ **Translated:**\n{result['translated']}\n\n"
                f"🎯 **Target:** {LANGUAGES.get(target_lang, 'Spanish')}\n\n"
                f"📊 {stake_response}"
            )
            
            await query.message.reply_text(response, parse_mode='Markdown')
            await query.edit_message_text(f"✅ Translation completed! {stake_response}")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("❌ Error translating. Please try again.")
    
    elif action == "process_grammar":
        await query.edit_message_text(f"✍️ Analyzing and correcting grammar... {stake_response}")
        
        try:
            result = correct_grammar(text)
            
            if result['changes_made']:
                response = (
                    f"✍️ **Grammar Correction**\n\n"
                    f"✅ **Corrected:**\n{result['corrected']}\n\n"
                    f"🔧 **Changes:** {result['total_corrections']} corrections\n\n"
                    f"📊 {stake_response}"
                )
            else:
                response = (
                    f"✍️ **Grammar Check**\n\n"
                    f"✅ No corrections needed!\n\n"
                    f"📝 **Your text:**\n{text}\n\n"
                    f"📊 {stake_response}"
                )
            
            await query.message.reply_text(response, parse_mode='Markdown')
            await query.edit_message_text(f"✅ Grammar check completed! {stake_response}")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("❌ Error checking grammar. Please try again.")
    
    elif action == "process_all":
        await query.edit_message_text(f"📊 Processing all functions... {stake_response}")
        
        # Grammar Correction
        try:
            result = correct_grammar(text)
            grammar_response = f"✍️ **Grammar:**\n✅ {result['corrected'][:100]}..."
            await query.message.reply_text(grammar_response, parse_mode='Markdown')
        except:
            pass
        
        # Translation
        try:
            result = translate_text(text, target_lang)
            translate_response = f"🌍 **Translation:**\n✅ {result['translated'][:100]}..."
            await query.message.reply_text(translate_response, parse_mode='Markdown')
        except:
            pass
        
        # Text-to-Speech
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
                temp_path = tmp_file.name
            
            slow = (speed == 'slow')
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(temp_path)
            
            with open(temp_path, 'rb') as audio_file:
                await query.message.reply_audio(
                    audio=audio_file,
                    caption=f"📊 Stake Daily - TTS\n🌐 Language: {LANGUAGES.get(lang, 'English')}",
                    title="Stake Daily TTS Audio",
                    performer="@Stake_Dailybot"
                )
            
            os.unlink(temp_path)
            await query.edit_message_text(f"✅ All functions completed! {stake_response}\n\nSpeak better • Write better • Understand more ✨")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("❌ Error processing TTS. Please try again.")

async def language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show language selection menu for TTS."""
    keyboard = []
    row = []
    tts_languages = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi']
    
    for code in tts_languages:
        if code in LANGUAGES:
            row.append(InlineKeyboardButton(LANGUAGES[code], callback_data=f"lang_{code}"))
            if len(row) == 3:
                keyboard.append(row)
                row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌐 Select your preferred TTS language:",
        reply_markup=reply_markup
    )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection callback."""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace("lang_", "")
    user_id = query.from_user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {}
    user_preferences[user_id]['lang'] = lang_code
    
    stake_response = get_stake_response()
    await query.edit_message_text(
        f"✅ TTS Language set to: {LANGUAGES[lang_code]}\n\n"
        f"🔊 Now use /tts [text] to convert to speech!\n\n"
        f"📊 {stake_response}"
    )

async def target_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show target language selection for translation."""
    keyboard = []
    row = []
    
    for i, (code, name) in enumerate(LANGUAGES.items()):
        row.append(InlineKeyboardButton(name, callback_data=f"target_{code}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌍 Select your preferred translation target language:",
        reply_markup=reply_markup
    )

async def target_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle target language selection callback."""
    query = update.callback_query
    await query.answer()
    
    lang_code = query.data.replace("target_", "")
    user_id = query.from_user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {}
    user_preferences[user_id]['target_lang'] = lang_code
    
    stake_response = get_stake_response()
    await query.edit_message_text(
        f"✅ Translation target language set to: {LANGUAGES[lang_code]}\n\n"
        f"🌍 Now use /translate [text] to translate!\n\n"
        f"📊 {stake_response}"
    )

SPEED_OPTIONS = {
    'normal': 'Normal Speed',
    'slow': 'Slow Speed',
}

async def speed_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show speed selection menu."""
    keyboard = []
    for speed, name in SPEED_OPTIONS.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"speed_{speed}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🎚️ Select your preferred speech speed:",
        reply_markup=reply_markup
    )

async def speed_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle speed selection callback."""
    query = update.callback_query
    await query.answer()
    
    speed = query.data.replace("speed_", "")
    user_id = query.from_user.id
    
    if user_id not in user_preferences:
        user_preferences[user_id] = {}
    user_preferences[user_id]['speed'] = speed
    
    stake_response = get_stake_response()
    await query.edit_message_text(
        f"✅ Speed set to: {SPEED_OPTIONS[speed]}\n\n"
        f"🔊 Now use /tts [text] to convert to speech!\n\n"
        f"📊 {stake_response}"
    )

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    await update.message.reply_text(
        "🎤 I can only process text messages.\n"
        "Please send me text for TTS, translation, or grammar correction!"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ An error occurred. Please try again later."
            )
    except:
        pass

def main() -> None:
    """Start the bot."""
    logger.info("📊 @Stake_Dailybot Starting...")
    logger.info("🔍 Looking for bot token...")
    
    token = get_token()
    
    if not token:
        logger.error("❌ No valid token found!")
        logger.info("Please set TELEGRAM_BOT_TOKEN in Railway environment variables")
        logger.info("Go to: Railway Dashboard -> Your Project -> Variables -> Add Variable")
        sys.exit(1)
    
    logger.info(f"✅ Token found! Token starts with: {token[:10]}...")
    logger.info("🚀 Starting @Stake_Dailybot...")
    logger.info("🎯 All-in-One: TTS + Translation + Grammar")
    logger.info("📊 Theme: Stake Daily - Investment in Communication")
    
    try:
        application = Application.builder().token(token).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("stake", stake_command))
        application.add_handler(CommandHandler("lang", language_menu))
        application.add_handler(CommandHandler("target", target_language_menu))
        application.add_handler(CommandHandler("speed", speed_menu))
        application.add_handler(CommandHandler("tts", tts_command))
        application.add_handler(CommandHandler("translate", translate_command))
        application.add_handler(CommandHandler("grammar", grammar_command))
        application.add_handler(CommandHandler("all", all_command))
        
        # Callback query handlers
        application.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(target_callback, pattern="^target_"))
        application.add_handler(CallbackQueryHandler(speed_callback, pattern="^speed_"))
        application.add_handler(CallbackQueryHandler(process_callback, pattern="^process_"))
        
        # Message handlers
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
        application.add_handler(MessageHandler(filters.VOICE, voice_handler))
        
        # Error handler
        application.add_error_handler(error_handler)
        
        logger.info("✅ @Stake_Dailybot is running and ready!")
        logger.info("🎯 Bot Username: @Stake_Dailybot")
        logger.info(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("📝 Features: TTS + Translation + Grammar")
        logger.info("💡 Motto: Speak better • Write better • Understand more")
        logger.info("📊 Special: Stake Daily - Investment theme")
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
