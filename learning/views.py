import random
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .ai_service import generate_tutor_reply
from .forms import QuizAnswerForm, SignUpForm, StartLearningForm, TutorPromptForm
from .models import *


# Multilingual UI Labels
LANGUAGE_UI_LABELS = {
    "Spanish": {
        "sign_up": "Registrarse",
        "my_profiles": "Mis Perfiles",
        "page_title": "Aprendizaje de Idiomas",
        "select_language_btn": "Iniciar Aprendizaje",
        "path_title": "Ruta de Aprendizaje",
        "quiz_header": "Prueba Rápida",
        "submit_btn": "Enviar",
        "all_options": "Todas las opciones se muestran en",
    },
    "French": {
        "sign_up": "S'inscrire",
        "my_profiles": "Mes Profils",
        "page_title": "Apprentissage des Langues",
        "select_language_btn": "Commencer à Apprendre",
        "path_title": "Chemin d'Apprentissage",
        "quiz_header": "Quiz Rapide",
        "submit_btn": "Soumettre",
        "all_options": "Toutes les options sont affichées en",
    },
    "German": {
        "sign_up": "Anmelden",
        "my_profiles": "Meine Profile",
        "page_title": "Sprachenlernen",
        "select_language_btn": "Lernen Starten",
        "path_title": "Lernpfad",
        "quiz_header": "Schnellquiz",
        "submit_btn": "Absenden",
        "all_options": "Alle Optionen werden angezeigt in",
    },
    "Italian": {
        "sign_up": "Iscriviti",
        "my_profiles": "I Miei Profili",
        "page_title": "Apprendimento delle Lingue",
        "select_language_btn": "Inizia ad Imparare",
        "path_title": "Percorso di Apprendimento",
        "quiz_header": "Quiz Veloce",
        "submit_btn": "Invia",
        "all_options": "Tutte le opzioni sono mostrate in",
    },
    "Portuguese": {
        "sign_up": "Inscrever-se",
        "my_profiles": "Meus Perfis",
        "page_title": "Aprendizado de Idiomas",
        "select_language_btn": "Começar a Aprender",
        "path_title": "Caminho de Aprendizado",
        "quiz_header": "Quiz Rápido",
        "submit_btn": "Enviar",
        "all_options": "Todas as opções são exibidas em",
    },
    "Japanese": {
        "sign_up": "登録",
        "my_profiles": "私のプロフィール",
        "page_title": "言語学習",
        "select_language_btn": "学習を開始",
        "path_title": "学習パス",
        "quiz_header": "クイズ",
        "submit_btn": "送信",
        "all_options": "すべてのオプションが表示されています",
    },
    "Korean": {
        "sign_up": "회원가입",
        "my_profiles": "내 프로필",
        "page_title": "언어 학습",
        "select_language_btn": "학습 시작",
        "path_title": "학습 경로",
        "quiz_header": "퀵 퀴즈",
        "submit_btn": "제출",
        "all_options": "모든 선택지는",
    },
    "Hindi": {
        "sign_up": "साइन अप करें",
        "my_profiles": "मेरी प्रोफाइलें",
        "page_title": "भाषा सीखना",
        "select_language_btn": "सीखना शुरू करें",
        "path_title": "सीखने का रास्ता",
        "quiz_header": "त्वरित प्रश्नोत्तरी",
        "submit_btn": "जमा करें",
        "all_options": "सभी विकल्प में दिखाए जाते हैं",
    },
    "Tamil": {
        "sign_up": "இணைந்து கொள்ளுங்கள்",
        "my_profiles": "எனது சுயவிவரங்கள்",
        "page_title": "மொழி கற்றல்",
        "select_language_btn": "கற்றல் தொடங்கவும்",
        "path_title": "கற்றல் பாதை",
        "quiz_header": "விரைவு வினாடி வினா",
        "submit_btn": "சமர்ப்பிக்கவும்",
        "all_options": "அனைத்து விருப்பங்களும் காட்டப்படுகின்றன",
    },
    "Chinese": {
        "sign_up": "注册",
        "my_profiles": "我的个人资料",
        "page_title": "语言学习",
        "select_language_btn": "开始学习",
        "path_title": "学习途径",
        "quiz_header": "快速测验",
        "submit_btn": "提交",
        "all_options": "所有选项都以",
    },
}

BILINGUAL_LESSONS = {
    "Spanish": {
        "code": "es",
        "description": "Learn practical Spanish with real bilingual phrases.",
        "lessons": [
            {
                "step": 0,
                "title": "The Spanish Alphabet",
                "difficulty": "beginner",
                "target": "A, B, C, D, E, F, G, H, I, J, K, L, M, N, Ñ, O, P, Q, R, S, T, U, V, W, X, Y, Z\n\nA: Abeja (bee)\nE: Elefante (elephant)\nI: Iglesia (church)\nO: Oso (bear)\nU: Uva (grape)",
                "english": "A, B, C, D, E, F, G, H, I, J, K, L, M, N, Ñ, O, P, Q, R, S, T, U, V, W, X, Y, Z\n\nA: Apple\nE: Elephant\nI: Ice cream\nO: Orange\nU: Umbrella",
                "activity_target": "Recita el alfabeto español en voz alta. Luego deletrea tu nombre.",
                "activity_english": "Recite Spanish alphabet aloud. Then spell your name.",
            },
            {
                "step": 1,
                "title": "Greetings & Introductions",
                "difficulty": "beginner",
                "target": "¡Hola! Me llamo Ana.\nBuenos días.\nMucho gusto.",
                "english": "Hello! My name is Ana.\nGood morning.\nNice to meet you.",
                "activity_target": "Greetings practice: Repeat 'Hola' and shake a friend's hand in the mirror.",
                "activity_english": "Greetings practice: Repeat and act it out.",
            },
            {
                "step": 2,
                "title": "Numbers & Time",
                "difficulty": "beginner",
                "target": "Uno, dos, tres, cuatro, cinco.\n¿Qué hora es?\nSon las tres.",
                "english": "One, two, three, four, five.\nWhat time is it?\nIt is three o'clock.",
                "activity_target": "Count to 10 in Spanish while clapping.",
                "activity_english": "Count to 10 while clapping.",
            },
            {
                "step": 3,
                "title": "Everyday Verbs",
                "difficulty": "beginner",
                "target": "Yo como pan.\nTú vas al parque.\nElla bebe agua.",
                "english": "I eat bread.\nYou go to the park.\nShe drinks water.",
                "activity_target": "Mime eating, going, drinking and say in Spanish.",
                "activity_english": "Act out while speaking.",
            },
            {
                "step": 4,
                "title": "Food & Ordering",
                "difficulty": "intermediate",
                "target": "Quisiera una pizza, por favor.\n¿Cuánto cuesta?\nEs delicioso.",
                "english": "I would like a pizza, please.\nHow much does it cost?\nIt is delicious.",
                "activity_target": "Role-play ordering at a Spanish restaurant.",
                "activity_english": "Roleplay restaurant ordering.",
            },
            {
                "step": 5,
                "title": "Travel & Directions",
                "difficulty": "intermediate",
                "target": "¿Dónde está la estación?\nA la izquierda, por favor.\nMuchas gracias.",
                "english": "Where is the station?\nTo the left, please.\nThank you very much.",
                "activity_target": "Ask for 5 different places around your house.",
                "activity_english": "Ask for 5 different places.",
            },
            {
                "step": 6,
                "title": "Opinions & Reactions",
                "difficulty": "advanced",
                "target": "Me gusta el café.\nNo me gusta la película.\nEstoy de acuerdo.",
                "english": "I like coffee.\nI don't like the movie.\nI agree.",
                "activity_target": "Express 5 opinions about food, movies, and weather.",
                "activity_english": "Express opinions about daily things.",
            },
            {
                "step": 7,
                "title": "Storytelling & Fluency",
                "difficulty": "advanced",
                "target": "Ayer fui al cine con mis amigos. Vimos una película interesante. Después, comimos helado.",
                "english": "Yesterday I went to the cinema with my friends. We watched an interesting movie. Afterwards, we ate ice cream.",
                "activity_target": "Tell a 3-sentence story about your day.",
                "activity_english": "Tell a short story about your day.",
            },
        ],
    },
    "French": {
        "code": "fr",
        "description": "Learn practical French with real bilingual phrases.",
        "lessons": [
            {
                "step": 0,
                "title": "The French Alphabet",
                "difficulty": "beginner",
                "target": "A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z\n\nA: Apple (Pomme)\nE: Éléphant\nI: Île (Island)\nO: Orange\nU: Université",
                "english": "A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z\n\nA: Apple\nE: Elephant\nI: Island\nO: Orange\nU: University",
                "activity_target": "Récitez l'alphabet français à haute voix. Puis épeler votre nom.",
                "activity_english": "Recite French alphabet aloud. Then spell your name.",
            },
            {
                "step": 1,
                "title": "Greetings & Introductions",
                "difficulty": "beginner",
                "target": "Bonjour, je m'appelle Marie.\nEnchanté.\nComment ça va?",
                "english": "Hello, my name is Marie.\nNice to meet you.\nHow are you?",
                "activity_target": "Introduce yourself to 3 people in French.",
                "activity_english": "Introduce yourself to 3 people.",
            },
            {
                "step": 2,
                "title": "Numbers & Time",
                "difficulty": "beginner",
                "target": "Un, deux, trois, quatre, cinq.\nQuelle heure est-il?\nIl est dix heures.",
                "english": "One, two, three, four, five.\nWhat time is it?\nIt is ten o'clock.",
                "activity_target": "Count to 10 in rapid French.",
                "activity_english": "Count to 10 rapidly.",
            },
            {
                "step": 3,
                "title": "Everyday Verbs",
                "difficulty": "beginner",
                "target": "Je vais à l'école.\nTu joues au football.\nIl danse bien.",
                "english": "I go to school.\nYou play football.\nHe dances well.",
                "activity_target": "Act out: going, playing, dancing in French.",
                "activity_english": "Act out actions.",
            },
            {
                "step": 4,
                "title": "Food & Ordering",
                "difficulty": "intermediate",
                "target": "Je voudrais un café, s'il vous plaît.\nCombien ça coûte?\nC'est délicieux!",
                "english": "I would like a coffee, please.\nHow much does it cost?\nIt is delicious!",
                "activity_target": "Order 5 items at a café in French.",
                "activity_english": "Order items at a café.",
            },
            {
                "step": 5,
                "title": "Travel & Directions",
                "difficulty": "intermediate",
                "target": "Où est la gare, s'il vous plaît?\nTournez à droite.\nMerci beaucoup.",
                "english": "Where is the station, please?\nTurn right.\nThank you very much.",
                "activity_target": "Ask for 5 locations in French.",
                "activity_english": "Ask for directions.",
            },
            {
                "step": 6,
                "title": "Opinions & Reactions",
                "difficulty": "advanced",
                "target": "J'aime la musique.\nJe n'aime pas les légumes.\nJe suis d'accord.",
                "english": "I like music.\nI don't like vegetables.\nI agree.",
                "activity_target": "Give 5 opinions about hobbies and food.",
                "activity_english": "Give opinions.",
            },
            {
                "step": 7,
                "title": "Storytelling & Fluency",
                "difficulty": "advanced",
                "target": "Hier, je suis allé au musée avec ma famille. C'était très beau. Nous avons pris des photos.",
                "english": "Yesterday, I went to the museum with my family. It was beautiful. We took photos.",
                "activity_target": "Tell a 3-sentence story in French.",
                "activity_english": "Tell a short story.",
            },
        ],
    },
    "German": {
        "code": "de",
        "description": "Learn practical German with real bilingual phrases.",
        "lessons": [
            {
                "step": 0,
                "title": "The German Alphabet",
                "difficulty": "beginner",
                "target": "A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z, Ä, Ö, Ü, ß\n\nA: Apfel (Apple)\nE: Elefant\nI: Inder\nO: Orange\nU: Uhr (Clock)",
                "english": "A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z, Ä, Ö, Ü, ß\n\nA: Apple\nE: Elephant\nI: Indian\nO: Orange\nU: Clock",
                "activity_target": "Rezitieren Sie das deutsche Alphabet laut auf. Dann buchstabieren Sie Ihren Namen.",
                "activity_english": "Recite German alphabet aloud. Then spell your name.",
            },
            {
                "step": 1,
                "title": "Greetings & Introductions",
                "difficulty": "beginner",
                "target": "Hallo, ich heiße Klaus.\nGuten Tag.\nEs freut mich.",
                "english": "Hello, my name is Klaus.\nGood day.\nNice to meet you.",
                "activity_target": "Greet 3 people with a handshake in German.",
                "activity_english": "Greet people.",
            },
            {
                "step": 2,
                "title": "Numbers & Time",
                "difficulty": "beginner",
                "target": "Eins, zwei, drei, vier, fünf.\nWie spät ist es?\nEs ist elf Uhr.",
                "english": "One, two, three, four, five.\nWhat time is it?\nIt is eleven o'clock.",
                "activity_target": "Count to 20 in German.",
                "activity_english": "Count to 20.",
            },
            {
                "step": 3,
                "title": "Everyday Verbs",
                "difficulty": "beginner",
                "target": "Ich esse Brot.\nDu gehst nach Hause.\nEr sitzt hier.",
                "english": "I eat bread.\nYou go home.\nHe sits here.",
                "activity_target": "Mime eating, walking, sitting in German.",
                "activity_english": "Act out actions.",
            },
            {
                "step": 4,
                "title": "Food & Ordering",
                "difficulty": "intermediate",
                "target": "Ich möchte ein Bier, bitte.\nWie viel kostet das?\nEs ist lecker!",
                "english": "I would like a beer, please.\nHow much does it cost?\nIt is tasty!",
                "activity_target": "Order at a German beer hall.",
                "activity_english": "Order at a restaurant.",
            },
            {
                "step": 5,
                "title": "Travel & Directions",
                "difficulty": "intermediate",
                "target": "Wo ist der Bahnhof, bitte?\nGo links.\nVielen Dank.",
                "english": "Where is the station, please?\nGo left.\nThank you very much.",
                "activity_target": "Ask for 5 locations in German.",
                "activity_english": "Ask for directions.",
            },
            {
                "step": 6,
                "title": "Opinions & Reactions",
                "difficulty": "advanced",
                "target": "Ich mag Fußball.\nIch mag nicht Spinat.\nIch bin einverstanden.",
                "english": "I like football.\nI don't like spinach.\nI agree.",
                "activity_target": "Express 5 opinions in German.",
                "activity_english": "Express opinions.",
            },
            {
                "step": 7,
                "title": "Storytelling & Fluency",
                "difficulty": "advanced",
                "target": "Gestern bin ich ins Kino gegangen. Der Film war großartig. Ich habe Popcorn gegessen.",
                "english": "Yesterday I went to the cinema. The movie was great. I ate popcorn.",
                "activity_target": "Tell a 3-sentence story in German.",
                "activity_english": "Tell a short story.",
            },
        ],
    },
    "Italian": {
        "code": "it",
        "description": "Learn practical Italian with real bilingual phrases.",
        "lessons": [
            {
                "step": 0,
                "title": "The Italian Alphabet",
                "difficulty": "beginner",
                "target": "A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z\n\nA: Albero (Tree)\nE: Elefante\nI: Isola (Island)\nO: Orange\nU: Università",
                "english": "A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z\n\nA: Tree\nE: Elephant\nI: Island\nO: Orange\nU: University",
                "activity_target": "Recita l'alfabeto italiano ad alta voce. Poi pronuncia il tuo nome lettera per lettera.",
                "activity_english": "Recite Italian alphabet aloud. Then spell your name.",
            },
            {
                "step": 1,
                "title": "Greetings & Introductions",
                "difficulty": "beginner",
                "target": "Ciao, mi chiamo Marco.\nBuongiorno.\nPiacere di conoscerti.",
                "english": "Hello, my name is Marco.\nGood morning.\nNice to meet you.",
                "activity_target": "Greet 3 people warmly in Italian.",
                "activity_english": "Greet people.",
            },
            {
                "step": 2,
                "title": "Numbers & Time",
                "difficulty": "beginner",
                "target": "Uno, due, tre, quattro, cinque.\nChe ora è?\nSono le quattro.",
                "english": "One, two, three, four, five.\nWhat time is it?\nIt is four o'clock.",
                "activity_target": "Count to 10 in Italian.",
                "activity_english": "Count to 10.",
            },
            {
                "step": 3,
                "title": "Everyday Verbs",
                "difficulty": "beginner",
                "target": "Io mangio pasta.\nTu balli bene.\nLui canta.",
                "english": "I eat pasta.\nYou dance well.\nHe sings.",
                "activity_target": "Act out: eating, dancing, singing in Italian.",
                "activity_english": "Act out actions.",
            },
            {
                "step": 4,
                "title": "Food & Ordering",
                "difficulty": "intermediate",
                "target": "Vorrei una pizza, per favore.\nQuanto costa?\nÈ squisito!",
                "english": "I would like a pizza, please.\nHow much does it cost?\nIt is exquisite!",
                "activity_target": "Order Italian food in Italian.",
                "activity_english": "Order food.",
            },
            {
                "step": 5,
                "title": "Travel & Directions",
                "difficulty": "intermediate",
                "target": "Dov'è la stazione, per favore?\nGira a sinistra.\nGrazie mille.",
                "english": "Where is the station, please?\nTurn left.\nThank you very much.",
                "activity_target": "Ask for 5 Italian locations.",
                "activity_english": "Ask for directions.",
            },
            {
                "step": 6,
                "title": "Opinions & Reactions",
                "difficulty": "advanced",
                "target": "Mi piace l'Italia.\nNon mi piace il formaggio.\nSono d'accordo.",
                "english": "I like Italy.\nI don't like cheese.\nI agree.",
                "activity_target": "Express 5 opinions in Italian.",
                "activity_english": "Express opinions.",
            },
            {
                "step": 7,
                "title": "Storytelling & Fluency",
                "difficulty": "advanced",
                "target": "Ieri sono andato in spiaggia con i miei amici. È stato bellissimo. Abbiamo mangiato gelato.",
                "english": "Yesterday I went to the beach with my friends. It was beautiful. We ate ice cream.",
                "activity_target": "Tell a 3-sentence story in Italian.",
                "activity_english": "Tell a short story.",
            },
        ],
    },
    "Portuguese": {
        "code": "pt",
        "description": "Learn practical Portuguese with real bilingual phrases.",
        "lessons": [
            {
                "step": 0,
                "title": "The Portuguese Alphabet",
                "difficulty": "beginner",
                "target": "A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z\n\nA: Árvore (Tree)\nE: Elefante\nI: Ilha (Island)\nO: Ovo (Egg)\nU: Uva (Grape)",
                "english": "A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z\n\nA: Tree\nE: Elephant\nI: Island\nO: Egg\nU: Grape",
                "activity_target": "Recite o alfabeto português em voz alta. Depois, soletra seu nome.",
                "activity_english": "Recite Portuguese alphabet aloud. Then spell your name.",
            },
            {
                "step": 1,
                "title": "Greetings & Introductions",
                "difficulty": "beginner",
                "target": "Olá, meu nome é João.\nBom dia.\nFico feliz em conhecê-lo.",
                "english": "Hello, my name is João.\nGood morning.\nI am happy to meet you.",
                "activity_target": "Greet 3 people in Portuguese.",
                "activity_english": "Greet people.",
            },
            {
                "step": 2,
                "title": "Numbers & Time",
                "difficulty": "beginner",
                "target": "Um, dois, três, quatro, cinco.\nQue horas são?\nSão duas horas.",
                "english": "One, two, three, four, five.\nWhat time is it?\nIt is two o'clock.",
                "activity_target": "Count to 10 in Portuguese.",
                "activity_english": "Count to 10.",
            },
            {
                "step": 3,
                "title": "Everyday Verbs",
                "difficulty": "beginner",
                "target": "Eu como arroz.\nVocê vai à praia.\nEla bebe café.",
                "english": "I eat rice.\nYou go to the beach.\nShe drinks coffee.",
                "activity_target": "Act out: eating, going, drinking.",
                "activity_english": "Act out actions.",
            },
            {
                "step": 4,
                "title": "Food & Ordering",
                "difficulty": "intermediate",
                "target": "Gostaria de uma cerveja, por favor.\nQuanto custa?\nÉ delicioso!",
                "english": "I would like a beer, please.\nHow much does it cost?\nIt is delicious!",
                "activity_target": "Order Brazilian food in Portuguese.",
                "activity_english": "Order food.",
            },
            {
                "step": 5,
                "title": "Travel & Directions",
                "difficulty": "intermediate",
                "target": "Onde fica a estação, por favor?\nVire à esquerda.\nMuito obrigado.",
                "english": "Where is the station, please?\nTurn left.\nThank you very much.",
                "activity_target": "Ask for 5 locations in Portuguese.",
                "activity_english": "Ask for directions.",
            },
            {
                "step": 6,
                "title": "Opinions & Reactions",
                "difficulty": "advanced",
                "target": "Gosto de futebol.\nNão gosto de brócolis.\nConcordo com você.",
                "english": "I like football.\nI don't like broccoli.\nI agree with you.",
                "activity_target": "Express 5 opinions in Portuguese.",
                "activity_english": "Express opinions.",
            },
            {
                "step": 7,
                "title": "Storytelling & Fluency",
                "difficulty": "advanced",
                "target": "Ontem fui à festa com os meus amigos. Dançamos até tarde. Comemos bolo delicioso.",
                "english": "Yesterday I went to the party with my friends. We danced until late. We ate delicious cake.",
                "activity_target": "Tell a 3-sentence story in Portuguese.",
                "activity_english": "Tell a short story.",
            },
        ],
    },
    "Japanese": {
        "code": "ja",
        "description": "Learn practical Japanese with real bilingual phrases.",
        "lessons": [
            {
                "step": 0,
                "title": "Hiragana & Katakana Scripts",
                "difficulty": "beginner",
                "target": "ひらがな (Hiragana): あ、い、う、え、お\nカタカナ (Katakana): ア、イ、ウ、エ、オ\n\nレッスン（Lesson）\nスポーツ（Sport）\nコンピューター（Computer）\nプラス（Plus）\nテレビ（Television）",
                "english": "Hiragana: a, i, u, e, o\nKatakana: a, i, u, e, o\n\nLesson (レッスン)\nSport (スポーツ)\nComputer (コンピューター)\n Plus (プラス)\nTelevision (テレビ)",
                "activity_target": "ひらがなの5つの基本音を繰り返す。その後、カタカナを練習する。",
                "activity_english": "Repeat the 5 basic Hiragana sounds. Then practice Katakana.",
            },
            {
                "step": 1,
                "title": "Greetings & Introductions",
                "difficulty": "beginner",
                "target": "こんにちは。私はタロウです。\n初めまして。\n会えてうれしい。",
                "english": "Hello. I am Taro.\nNice to meet you.\nI am happy to meet you.",
                "activity_target": "Greet 3 people in Japanese with a bow.",
                "activity_english": "Greet people.",
            },
            {
                "step": 2,
                "title": "Numbers & Time",
                "difficulty": "beginner",
                "target": "一、二、三、四、五。\n今、何時ですか？\n午後3時です。",
                "english": "One, two, three, four, five.\nWhat time is it now?\nIt is 3 PM.",
                "activity_target": "Count to 10 in Japanese.",
                "activity_english": "Count to 10.",
            },
            {
                "step": 3,
                "title": "Everyday Verbs",
                "difficulty": "beginner",
                "target": "私はご飯を食べます。\nあなたは走ります。\n彼は寝ます。",
                "english": "I eat rice.\nYou run.\nHe sleeps.",
                "activity_target": "Act out: eating, running, sleeping.",
                "activity_english": "Act out actions.",
            },
            {
                "step": 4,
                "title": "Food & Ordering",
                "difficulty": "intermediate",
                "target": "すしをください。\nいくらですか？\nおいしいです！",
                "english": "Give me sushi, please.\nHow much is it?\nIt is delicious!",
                "activity_target": "Order Japanese food politely.",
                "activity_english": "Order food.",
            },
            {
                "step": 5,
                "title": "Travel & Directions",
                "difficulty": "intermediate",
                "target": "駅はどこですか？\n左に曲がってください。\nありがとうございます。",
                "english": "Where is the station?\nTurn left, please.\nThank you very much.",
                "activity_target": "Ask for 5 locations in Japanese.",
                "activity_english": "Ask for directions.",
            },
            {
                "step": 6,
                "title": "Opinions & Reactions",
                "difficulty": "advanced",
                "target": "私はサッカーが好きです。\n野菜が嫌いです。\nそうですね。",
                "english": "I like football.\nI don't like vegetables.\nYou're right.",
                "activity_target": "Express 5 opinions in Japanese.",
                "activity_english": "Express opinions.",
            },
            {
                "step": 7,
                "title": "Storytelling & Fluency",
                "difficulty": "advanced",
                "target": "昨日、映画館に行きました。面白い映画でした。その後、友達とコーヒーを飲みました。",
                "english": "Yesterday I went to the cinema. It was an interesting movie. Afterwards, I drank coffee with my friend.",
                "activity_target": "Tell a 3-sentence story in Japanese.",
                "activity_english": "Tell a short story.",
            },
        ],
    },
    "Korean": {
        "code": "ko",
        "description": "Learn practical Korean with real bilingual phrases.",
        "lessons": [
            {
                "step": 0,
                "title": "Hangul Alphabet (한글)",
                "difficulty": "beginner",
                "target": "기본 자음: ㄱ, ㄴ, ㄷ, ㄹ, ㅁ, ㅂ, ㅅ\n기본 모음: ㅏ, ㅑ, ㅓ, ㅕ, ㅗ\n\n가 (ga) - Apple\n나 (na) - Pear\n다 (da) - Nothing\n라 (ra) - Come\n마 (ma) - Horse",
                "english": "Basic Consonants: g, n, d, r, m, b, s\nBasic Vowels: a, ya, eo, yeo, o\n\nGa - Apple\nNa - Pear\nDa - Nothing\nRa - Come\nMa - Horse",
                "activity_target": "한글의 기본 자음과 모음을 5번씩 반복한다. 그 후 간단한 단어를 만들어본다.",
                "activity_english": "Repeat basic Hangul consonants and vowels 5 times each. Then make simple words.",
            },
            {
                "step": 1,
                "title": "Greetings & Introductions",
                "difficulty": "beginner",
                "target": "안녕하세요. 제 이름은 미영입니다.\n처음 뵙겠습니다.\n만나서 반갑습니다.",
                "english": "Hello. My name is Mi-young.\nNice to meet you for the first time.\nI am happy to meet you.",
                "activity_target": "Greet 3 people in Korean with a bow.",
                "activity_english": "Greet people.",
            },
            {
                "step": 2,
                "title": "Numbers & Time",
                "difficulty": "beginner",
                "target": "하나, 둘, 셋, 넷, 다섯.\n지금 몇 시예요?\n오후 3시예요.",
                "english": "One, two, three, four, five.\nWhat time is it?\nIt is 3 PM.",
                "activity_target": "Count to 10 in Korean.",
                "activity_english": "Count to 10.",
            },
            {
                "step": 3,
                "title": "Everyday Verbs",
                "difficulty": "beginner",
                "target": "저는 밥을 먹어요.\n너는 달려요.\n그는 자요.",
                "english": "I eat rice.\nYou run.\nHe sleeps.",
                "activity_target": "Act out: eating, running, sleeping.",
                "activity_english": "Act out actions.",
            },
            {
                "step": 4,
                "title": "Food & Ordering",
                "difficulty": "intermediate",
                "target": "김밥을 주세요.\n얼마예요?\n맛있어요!",
                "english": "Give me kimbap, please.\nHow much is it?\nIt is delicious!",
                "activity_target": "Order Korean food politely.",
                "activity_english": "Order food.",
            },
            {
                "step": 5,
                "title": "Travel & Directions",
                "difficulty": "intermediate",
                "target": "역이 어디예요?\n왼쪽으로 가세요.\n고마워요.",
                "english": "Where is the station?\nGo left, please.\nThank you.",
                "activity_target": "Ask for 5 locations in Korean.",
                "activity_english": "Ask for directions.",
            },
            {
                "step": 6,
                "title": "Opinions & Reactions",
                "difficulty": "advanced",
                "target": "저는 축구를 좋아해요.\n야채를 싫어해요.\n동의해요.",
                "english": "I like football.\nI don't like vegetables.\nI agree.",
                "activity_target": "Express 5 opinions in Korean.",
                "activity_english": "Express opinions.",
            },
            {
                "step": 7,
                "title": "Storytelling & Fluency",
                "difficulty": "advanced",
                "target": "어제 영화관에 갔어요. 재미있는 영화였어요. 그 후에 친구와 커피를 마셨어요.",
                "english": "Yesterday I went to the cinema. It was a fun movie. Afterwards, I drank coffee with my friend.",
                "activity_target": "Tell a 3-sentence story in Korean.",
                "activity_english": "Tell a short story.",
            },
        ],
    },
    "Hindi": {
        "code": "hi",
        "description": "Learn practical Hindi with real bilingual phrases.",
        "lessons": [
            {
                "step": 0,
                "title": "Devanagari Script & Basic Sounds",
                "difficulty": "beginner",
                "target": "स्वर (Swara - Vowels): अ, आ, इ, ई, उ, ऊ\nव्यंजन (Consonants - First 5): क, ख, ग, घ, ङ\n\nक (ka) - कमल (Kamal - Lotus)\nख (kha) - खरगोश (Khargosh - Rabbit)\nग (ga) - गाय (Gaay - Cow)\nघ (gha) - घोड़ा (Ghora - Horse)\nङ (nga) - हंसना (Hansna - To laugh)",
                "english": "Vowels (Swara): a, aa, i, ii, u, uu\nConsonants (First 5): ka, kha, ga, gha, nga\n\nKa - Lotus\nKha - Rabbit\nGa - Cow\nGha - Horse\nNga - To laugh",
                "activity_target": "देवनागरी लिपि के 5 बुनियादी स्वर और व्यंजन को दोहराएं। फिर सरल शब्द बनाने की कोशिश करें।",
                "activity_english": "Repeat 5 basic Devanagari vowels and consonants. Then try making simple words.",
            },
            {
                "step": 1,
                "title": "Greetings & Introductions",
                "difficulty": "beginner",
                "target": "नमस्ते, मेरा नाम राज है।\nआपसे मिलकर खुशी हुई।\nआप कैसे हो?",
                "english": "Hello, my name is Raj.\nNice to meet you.\nHow are you?",
                "activity_target": "Greet 3 people in Hindi with folded hands.",
                "activity_english": "Greet people.",
            },
            {
                "step": 2,
                "title": "Numbers & Time",
                "difficulty": "beginner",
                "target": "एक, दो, तीन, चार, पाँच।\nयह कितना बजा है?\nतीन बजे हैं।",
                "english": "One, two, three, four, five.\nWhat time is it?\nIt is three o'clock.",
                "activity_target": "Count to 10 in Hindi.",
                "activity_english": "Count to 10.",
            },
            {
                "step": 3,
                "title": "Everyday Verbs",
                "difficulty": "beginner",
                "target": "मैं खाना खाता हूँ।\nतुम दौड़ते हो।\nवह सोता है।",
                "english": "I eat food.\nYou run.\nHe sleeps.",
                "activity_target": "Act out: eating, running, sleeping.",
                "activity_english": "Act out actions.",
            },
            {
                "step": 4,
                "title": "Food & Ordering",
                "difficulty": "intermediate",
                "target": "मुझे चाय दीजिए, कृपया।\nयह कितना है?\nबहुत स्वादिष्ट है!",
                "english": "Give me tea, please.\nHow much is it?\nIt is very tasty!",
                "activity_target": "Order Indian food politely.",
                "activity_english": "Order food.",
            },
            {
                "step": 5,
                "title": "Travel & Directions",
                "difficulty": "intermediate",
                "target": "रेलवे स्टेशन कहाँ है?\nबाईं ओर मुड़ें।\nधन्यवाद।",
                "english": "Where is the railway station?\nTurn left.\nThank you.",
                "activity_target": "Ask for 5 locations in Hindi.",
                "activity_english": "Ask for directions.",
            },
            {
                "step": 6,
                "title": "Opinions & Reactions",
                "difficulty": "advanced",
                "target": "मुझे फुटबॉल पसंद है।\nमुझे सब्जियाँ पसंद नहीं हैं।\nमैं सहमत हूँ।",
                "english": "I like football.\nI don't like vegetables.\nI agree.",
                "activity_target": "Express 5 opinions in Hindi.",
                "activity_english": "Express opinions.",
            },
            {
                "step": 7,
                "title": "Storytelling & Fluency",
                "difficulty": "advanced",
                "target": "कल मैं सिनेमा गया। यह एक अच्छी फिल्म थी। उसके बाद मैंने अपने दोस्त के साथ चाय पी।",
                "english": "Yesterday I went to the cinema. It was a good movie. Afterwards, I had tea with my friend.",
                "activity_target": "Tell a 3-sentence story in Hindi.",
                "activity_english": "Tell a short story.",
            },
        ],
    },
    "Tamil": {
        "code": "ta",
        "description": "Learn practical Tamil with real bilingual phrases.",
        "lessons": [
            {
                "step": 0,
                "title": "Tamil Script & Basic Sounds",
                "difficulty": "beginner",
                "target": "உயிர் எழுத்துக்கள் (Vowels): அ, ஆ, இ, ஈ, உ, ஊ\nமெய் எழுத்துக்கள் (Consonants - First 5): க, ங, ச, ஞ, ட\n\nக (ka) - கண் (Kan - Eye)\nங (nga) - நாங்கள் (Nangal - We)\nச (cha) - சாப்பிடு (Saapidu - To eat)\nஞ (nya) - மஞ்சள் (Manju - Turmeric)\nட (ta) - தண்ணீர் (Thanneer - Water)",
                "english": "Vowels: a, aa, i, ii, u, uu\nConsonants (First 5): ka, nga, cha, nya, ta\n\nKa - Eye\nNga - We\nCha - To eat\nNya - Turmeric\nTa - Water",
                "activity_target": "தமிழ் எழுத்துக்களின் 5 கூறுகளை 5 முறை மீண்டும் கூறுங்கள். பிறகு எளிய சொற்களை உருவாக்க முயற்சிக்கவும்.",
                "activity_english": "Repeat 5 basic Tamil sounds 5 times each. Then try making simple words.",
            },
            {
                "step": 1,
                "title": "Greetings & Introductions",
                "difficulty": "beginner",
                "target": "வணக்கம், என் பெயர் முரளி.\nநீங்களை சந்திக்க எனக்கு மகிழ்ச்சி.\nநீங்கள் எப்படி இருக்கிறீர்கள்?",
                "english": "Hello, my name is Murali.\nI am happy to meet you.\nHow are you?",
                "activity_target": "Greet 3 people in Tamil.",
                "activity_english": "Greet people.",
            },
            {
                "step": 2,
                "title": "Numbers & Time",
                "difficulty": "beginner",
                "target": "ஒன்று, இரண்டு, மூன்று, நான்கு, ஐந்து.\nஇப்போது என்ன நேரம்?\nமூன்று மணி.",
                "english": "One, two, three, four, five.\nWhat time is it now?\nThree o'clock.",
                "activity_target": "Count to 10 in Tamil.",
                "activity_english": "Count to 10.",
            },
            {
                "step": 3,
                "title": "Everyday Verbs",
                "difficulty": "beginner",
                "target": "நான் சாப்பிடுகிறேன்.\nநீ ஓடுகிறாய்.\nஅவன் படுக்கிறான்.",
                "english": "I eat.\nYou run.\nHe sleeps.",
                "activity_target": "Act out: eating, running, sleeping.",
                "activity_english": "Act out actions.",
            },
            {
                "step": 4,
                "title": "Food & Ordering",
                "difficulty": "intermediate",
                "target": "எனக்கு தோசை தாருங்கள்.\nவிலை என்ன?\nபहुत맛்டுத்தியாக்க இருக்கிறது!",
                "english": "Give me dosa, please.\nWhat is the price?\nIt is delicious!",
                "activity_target": "Order Tamil food politely.",
                "activity_english": "Order food.",
            },
            {
                "step": 5,
                "title": "Travel & Directions",
                "difficulty": "intermediate",
                "target": "ரயில் நிலையம் எங்கே?\nஇடப்புறம் திரும்பிக்கோ.\nநன்றி.",
                "english": "Where is the railway station?\nTurn left.\nThank you.",
                "activity_target": "Ask for 5 locations in Tamil.",
                "activity_english": "Ask for directions.",
            },
            {
                "step": 6,
                "title": "Opinions & Reactions",
                "difficulty": "advanced",
                "target": "எனக்கு கிரிக்கெட் பிடிக்கும்.\nஎனக்கு காய்கறி பிடிக்கவில்லை.\nநான் ஒப்புக்கொள்கிறேன்.",
                "english": "I like cricket.\nI don't like vegetables.\nI agree.",
                "activity_target": "Express 5 opinions in Tamil.",
                "activity_english": "Express opinions.",
            },
            {
                "step": 7,
                "title": "Storytelling & Fluency",
                "difficulty": "advanced",
                "target": "நேற்று நான் சினிமாவுக்குப் போனேன். அது ஒரு நல்ல படமாக இருந்தது. பின்பு நான் என் நண்பனுடன் கொண்டை சாப்பிட்டேன்.",
                "english": "Yesterday I went to the cinema. It was a good movie. Afterwards, I ate konda with my friend.",
                "activity_target": "Tell a 3-sentence story in Tamil.",
                "activity_english": "Tell a short story.",
            },
        ],
    },
    "Chinese": {
        "code": "zh",
        "description": "Learn practical Chinese with real bilingual phrases.",
        "lessons": [
            {
                "step": 0,
                "title": "Chinese Characters & Pinyin",
                "difficulty": "beginner",
                "target": "拼音基础 (Pinyin Basics):\na, o, e, i, u, ü\n\n常用汉字 (Common Characters):\n一 (yi) - One\n二 (er) - Two\n三 (san) - Three\n人 (ren) - Person\n大 (da) - Big",
                "english": "Pinyin Basics:\na, o, e, i, u, ü\n\nCommon Characters:\n一 (yi) - One\n二 (er) - Two\n三 (san) - Three\n人 (ren) - Person\n大 (da) - Big",
                "activity_target": "重复拼音基础音5次。然后用手指写5个基本汉字。",
                "activity_english": "Repeat Pinyin basic sounds 5 times. Then trace 5 basic Chinese characters.",
            },
            {
                "step": 1,
                "title": "Greetings & Introductions",
                "difficulty": "beginner",
                "target": "你好，我叫王小明。\n很高兴认识你。\n你好吗？",
                "english": "Hello, my name is Wang Xiaoming.\nNice to meet you.\nHow are you?",
                "activity_target": "Greet 3 people in Mandarin.",
                "activity_english": "Greet people.",
            },
            {
                "step": 2,
                "title": "Numbers & Time",
                "difficulty": "beginner",
                "target": "一、二、三、四、五。\n现在几点？\n下午三点。",
                "english": "One, two, three, four, five.\nWhat time is it?\nIt is 3 PM.",
                "activity_target": "Count to 10 in Mandarin.",
                "activity_english": "Count to 10.",
            },
            {
                "step": 3,
                "title": "Everyday Verbs",
                "difficulty": "beginner",
                "target": "我吃米饭。\n你跑步。\n他睡觉。",
                "english": "I eat rice.\nYou run.\nHe sleeps.",
                "activity_target": "Act out: eating, running, sleeping.",
                "activity_english": "Act out actions.",
            },
            {
                "step": 4,
                "title": "Food & Ordering",
                "difficulty": "intermediate",
                "target": "请给我一碗面。\n多少钱？\n很好吃！",
                "english": "Give me a bowl of noodles, please.\nHow much is it?\nIt is delicious!",
                "activity_target": "Order Chinese food politely.",
                "activity_english": "Order food.",
            },
            {
                "step": 5,
                "title": "Travel & Directions",
                "difficulty": "intermediate",
                "target": "火车站在哪里？\n向左转。\n谢谢你。",
                "english": "Where is the train station?\nTurn left.\nThank you.",
                "activity_target": "Ask for 5 locations in Mandarin.",
                "activity_english": "Ask for directions.",
            },
            {
                "step": 6,
                "title": "Opinions & Reactions",
                "difficulty": "advanced",
                "target": "我喜欢足球。\n我不喜欢蔬菜。\n我同意。",
                "english": "I like football.\nI don't like vegetables.\nI agree.",
                "activity_target": "Express 5 opinions in Mandarin.",
                "activity_english": "Express opinions.",
            },
            {
                "step": 7,
                "title": "Storytelling & Fluency",
                "difficulty": "advanced",
                "target": "昨天我去了电影院。那是一部很好的电影。之后我和朋友喝了茶。",
                "english": "Yesterday I went to the cinema. It was a great movie. Afterwards, I drank tea with my friend.",
                "activity_target": "Tell a 3-sentence story in Mandarin.",
                "activity_english": "Tell a short story.",
            },
        ],
    },
}


def _seed_platform_data():
    # Common distractor phrases for quizzes (in various languages)
    quiz_distractors = {
        "Spanish": ["Adiós", "Por favor", "Gracias", "Sí", "No", "Quizás"],
        "French": ["Au revoir", "S'il vous plaît", "Merci", "Oui", "Non", "Peut-être"],
        "German": ["Auf Wiedersehen", "Bitte", "Danke", "Ja", "Nein", "Vielleicht"],
        "Italian": ["Arrivederci", "Per favore", "Grazie", "Sì", "No", "Forse"],
        "Portuguese": ["Adeus", "Por favor", "Obrigado", "Sim", "Não", "Talvez"],
        "Japanese": ["さようなら", "お願いします", "ありがとう", "はい", "いいえ", "多分"],
        "Korean": ["안녕히 가세요", "부탁합니다", "감사합니다", "네", "아니오", "아마도"],
        "Hindi": ["अलविदा", "कृपया", "धन्यवाद", "हाँ", "नहीं", "शायद"],
        "Tamil": ["பிரிவு", "தயவுசெய்து", "நன்றி", "ஆம்", "இல்லை", "பொதுவாக"],
        "Chinese": ["再见", "请", "谢谢", "是", "否", "也许"],
    }
    
    for language_name, language_data in BILINGUAL_LESSONS.items():
        language, _ = Language.objects.get_or_create(
            code=language_data["code"],
            defaults={
                "name": language_name,
                "description": language_data["description"],
            },
        )

        if language.name != language_name or language.description != language_data["description"]:
            language.name = language_name
            language.description = language_data["description"]
            language.save(update_fields=["name", "description"])

        for lesson_data in language_data["lessons"]:
            lesson, _ = Lesson.objects.update_or_create(
                language=language,
                step_number=lesson_data["step"],
                defaults={
                    "title": lesson_data["title"],
                    "content": f"{lesson_data['title']}: Learn key phrases.",
                    "content_target_language": lesson_data["target"],
                    "content_english": lesson_data["english"],
                    "funny_activity": lesson_data["activity_english"],
                    "funny_activity_target_language": lesson_data["activity_target"],
                    "difficulty": lesson_data["difficulty"],
                },
            )
            
            # Generate bilingual quiz with meaningful target-language options
            correct_answer = lesson_data["target"].split("\n")[0]
            distractors = random.sample(quiz_distractors.get(language_name, ["Option 1", "Option 2", "Option 3"]), 3)
            options = [correct_answer] + distractors
            random.shuffle(options)
            
            # Find correct option letter
            correct_idx = options.index(correct_answer)
            correct_letter = chr(65 + correct_idx)  # A=65 in ASCII
            
            option_dict = {
                "A": options[0],
                "B": options[1],
                "C": options[2],
                "D": options[3],
            }
            
            QuizQuestion.objects.update_or_create(
                lesson=lesson,
                defaults={
                    "prompt": f"Translate to {language_name}: '{lesson_data['english'].split(chr(10))[0]}'",
                    "option_a": option_dict["A"],
                    "option_b": option_dict["B"],
                    "option_c": option_dict["C"],
                    "option_d": option_dict["D"],
                    "correct_option": correct_letter,
                },
            )


def _ai_fun_coach(profile):
    jokes = [
        "You are not making mistakes. You are collecting plot twists for fluency.",
        "If grammar was a gym, you just finished leg day. Strong work.",
        "Your vocabulary is leveling up faster than a game character with bonus XP.",
        "Your accent is your signature style. Keep speaking boldly.",
    ]

    score = profile.performance_score
    if score < 30:
        mission = "Mission: Complete 1 lesson + 1 quiz today. Reward yourself with a victory snack."
    elif score < 60:
        mission = "Mission: Build 5 original sentences from today lesson and read them out loud."
    elif score < 85:
        mission = "Mission: Record a 60-second self-introduction and improve pronunciation."
    else:
        mission = "Mission: Teach a friend one mini topic. Teaching locks mastery."

    return {
        "message": random.choice(jokes),
        "mission": mission,
        "next_level_hint": f"Current level: {profile.level}. Reach 90+ score for Master tier.",
    }


def _award_badges(profile):
    badge_rules = [
        {
            "title": "First Step",
            "description": "Completed your first structured lesson.",
            "condition": profile.completed_lessons >= 1,
        },
        {
            "title": "Accuracy Ace",
            "description": "Reached at least 70% quiz accuracy.",
            "condition": profile.accuracy >= 70,
        },
        {
            "title": "Speaker Tier",
            "description": "Reached Speaker level with strong consistency.",
            "condition": profile.level in ["Speaker", "Master"],
        },
        {
            "title": "Master Tier",
            "description": "Reached Master level with elite performance.",
            "condition": profile.level == "Master",
        },
    ]

    for rule in badge_rules:
        if rule["condition"]:
            BadgeAward.objects.get_or_create(
                learner=profile,
                title=rule["title"],
                defaults={"description": rule["description"]},
            )


def _ensure_profile_access(request, profile):
    if profile.user_id and (not request.user.is_authenticated or profile.user_id != request.user.id):
        raise PermissionDenied("This profile belongs to another account.")

    # Claim legacy profile automatically for matching logged-in username.
    if request.user.is_authenticated and profile.user_id is None and profile.name == request.user.username:
        profile.user = request.user
        profile.save(update_fields=["user"])


def _resolve_tutor_question(profile, prompt_text):
    response = generate_tutor_reply(profile.language.name, profile.level, prompt_text)
    TutorInteraction.objects.create(
        learner=profile,
        prompt=prompt_text,
        response=response["reply"],
        provider=response["provider"],
        used_external_ai=response["used_external_ai"],
    )
    return response


def signup(request):
    if request.user.is_authenticated:
        return redirect("learning:home")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. Start your language track.")
            return redirect("learning:home")
    else:
        form = SignUpForm()

    context = {
        "form": form,
        "nav_label": "회원가입",  # Korean: Sign Up
    }
    return render(request, "learning/signup.html", context)


@login_required
def my_profiles(request):
    profiles = LearnerProfile.objects.filter(user=request.user).select_related("language")
    context = {
        "profiles": profiles,
        "nav_label": "내 프로필",  # Korean: My Profiles
    }
    return render(request, "learning/my_profiles.html", context)


@login_required
def home(request):
    _seed_platform_data()

    if request.method == "POST":
        post_data = request.POST.copy()
        if request.user.is_authenticated and not post_data.get("name"):
            post_data["name"] = request.user.username
        form = StartLearningForm(post_data)
        if form.is_valid():
            language = form.cleaned_data["language"]
            name = request.user.username
            profile = LearnerProfile.objects.filter(user=request.user, language=language).first()
            if not profile:
                profile = LearnerProfile.objects.filter(user__isnull=True, name=name, language=language).first()
                if profile:
                    profile.user = request.user
                    profile.save(update_fields=["user"])

            if not profile:
                try:
                    with transaction.atomic():
                        profile = LearnerProfile.objects.create(user=request.user, name=name, language=language)
                except IntegrityError:
                    # Recover from legacy/conflicting rows so the flow still reaches learning path.
                    profile = LearnerProfile.objects.filter(user=request.user, language=language).first()
                    if not profile:
                        by_name = LearnerProfile.objects.filter(name=name, language=language).first()
                        if by_name and by_name.user_id is None:
                            by_name.user = request.user
                            by_name.save(update_fields=["user"])
                            profile = by_name

            if not profile:
                messages.error(request, "Could not start this learning path. Please try again.")
                return redirect("learning:home")

            return redirect("learning:language_detail", language_id=language.id, profile_id=profile.id)
        messages.error(request, "Please choose a language to continue.")
    else:
        form = StartLearningForm(initial={"name": request.user.username})

    languages = Language.objects.annotate(total_lessons=Count("lessons"))
    my_profiles_data = LearnerProfile.objects.filter(user=request.user).select_related("language")

    context = {
        "form": form,
        "languages": languages,
        "my_profiles": my_profiles_data,
        "page_title": "언어 학습",  # Korean: Language Learning
        "select_language_btn": "학습 시작",  # Korean: Start Learning
    }
    return render(request, "learning/home.html", context)


@login_required
def language_detail(request, language_id, profile_id):
    language = get_object_or_404(Language, id=language_id)
    profile = get_object_or_404(LearnerProfile, id=profile_id, language=language)
    
    # Ensure user owns this profile
    if profile.user_id != request.user.id:
        raise PermissionDenied("This profile belongs to another account.")
    
    lessons = Lesson.objects.filter(language=language)

    ai_tips = _ai_fun_coach(profile)
    latest_tutor_chat = TutorInteraction.objects.filter(learner=profile).first()
    ui_labels = LANGUAGE_UI_LABELS.get(language.name, {})

    context = {
        "language": language,
        "profile": profile,
        "lessons": lessons,
        "ai_tips": ai_tips,
        "next_step": profile.completed_lessons + 1,
        "total_steps": lessons.count(),
        "tutor_form": TutorPromptForm(),
        "latest_tutor_chat": latest_tutor_chat,
        "page_title": ui_labels.get("path_title", "Learning Path"),
        "ui_labels": ui_labels,
    }
    return render(request, "learning/language_detail.html", context)


@login_required
def lesson_detail(request, language_id, profile_id, lesson_id):
    language = get_object_or_404(Language, id=language_id)
    profile = get_object_or_404(LearnerProfile, id=profile_id, language=language)
    
    # Ensure user owns this profile
    if profile.user_id != request.user.id:
        raise PermissionDenied("This profile belongs to another account.")
    
    lesson = get_object_or_404(Lesson, id=lesson_id, language=language)

    allowed_step = profile.completed_lessons + 1
    if lesson.step_number > allowed_step:
        messages.warning(request, "Finish previous steps first to keep learning structured.")
        return redirect("learning:language_detail", language_id=language.id, profile_id=profile.id)

    question = getattr(lesson, "question", None)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "complete_lesson" and lesson.step_number == allowed_step:
            profile.completed_lessons += 1
            profile.save(update_fields=["completed_lessons", "updated_at"])
            _award_badges(profile)
            PerformanceLog.objects.create(
                learner=profile,
                lesson=lesson,
                is_correct=True,
                points=10,
                notes="Completed lesson step",
            )
            messages.success(request, "Lesson completed. Great consistency.")
            return redirect("learning:lesson_detail", language_id=language.id, profile_id=profile.id, lesson_id=lesson.id)

        if action == "submit_quiz" and question:
            form = QuizAnswerForm(request.POST)
            if form.is_valid():
                selected = form.cleaned_data["selected_option"]
                is_correct = selected == question.correct_option

                profile.quiz_attempts += 1
                if is_correct:
                    profile.correct_answers += 1
                profile.save(update_fields=["quiz_attempts", "correct_answers", "updated_at"])
                _award_badges(profile)

                PerformanceLog.objects.create(
                    learner=profile,
                    lesson=lesson,
                    question=question,
                    is_correct=is_correct,
                    points=15 if is_correct else 2,
                    notes="Quiz evaluation",
                )

                if is_correct:
                    messages.success(request, "Correct answer. You are growing fast.")
                else:
                    messages.error(
                        request,
                        f"Not correct this time. Right answer: {question.correct_option}. Keep going.",
                    )
                return redirect("learning:lesson_detail", language_id=language.id, profile_id=profile.id, lesson_id=lesson.id)
        else:
            form = QuizAnswerForm(initial={"question_id": question.id})
    else:
        form = QuizAnswerForm(initial={"question_id": question.id}) if question else None

    context = {
        "language": language,
        "profile": profile,
        "lesson": lesson,
        "question": question,
        "quiz_form": form,
        "is_completed": lesson.step_number <= profile.completed_lessons,
        "can_mark_complete": lesson.step_number == profile.completed_lessons + 1,
        "ui_labels": LANGUAGE_UI_LABELS.get(language.name, {}),
    }
    return render(request, "learning/lesson_detail.html", context)


@login_required
def dashboard(request, profile_id):
    profile = get_object_or_404(LearnerProfile, id=profile_id)
    
    # Ensure user owns this profile
    if profile.user_id != request.user.id:
        raise PermissionDenied("This profile belongs to another account.")
    
    _award_badges(profile)

    total_lessons = Lesson.objects.filter(language=profile.language).count()
    completion_percent = 0
    if total_lessons:
        completion_percent = round((profile.completed_lessons / total_lessons) * 100, 1)

    logs = PerformanceLog.objects.filter(learner=profile)[:12]
    ai_tips = _ai_fun_coach(profile)
    badges = BadgeAward.objects.filter(learner=profile)
    latest_tutor_chat = TutorInteraction.objects.filter(learner=profile).first()
    can_get_certificate = profile.level in ["Speaker", "Master"]

    context = {
        "profile": profile,
        "total_lessons": total_lessons,
        "completion_percent": completion_percent,
        "logs": logs,
        "ai_tips": ai_tips,
        "badges": badges,
        "tutor_form": TutorPromptForm(),
        "latest_tutor_chat": latest_tutor_chat,
        "can_get_certificate": can_get_certificate,
    }
    return render(request, "learning/dashboard.html", context)


@login_required
def ask_tutor(request, profile_id):
    profile = get_object_or_404(LearnerProfile, id=profile_id)
    
    # Ensure user owns this profile
    if profile.user_id != request.user.id:
        raise PermissionDenied("This profile belongs to another account.")

    if request.method != "POST":
        return redirect("learning:dashboard", profile_id=profile.id)

    form = TutorPromptForm(request.POST)
    next_url = request.POST.get("next") or redirect("learning:dashboard", profile_id=profile.id).url
    if form.is_valid():
        prompt_text = form.cleaned_data["prompt"].strip()
        response = _resolve_tutor_question(profile, prompt_text)
        provider_text = response["provider"]
        messages.success(request, f"AI tutor replied via {provider_text}.")
    else:
        messages.error(request, "Please type a tutor question first.")

    return redirect(next_url)


@login_required
def certificate(request, profile_id):
    profile = get_object_or_404(LearnerProfile, id=profile_id)
    
    # Ensure user owns this profile
    if profile.user_id != request.user.id:
        raise PermissionDenied("This profile belongs to another account.")
    
    _award_badges(profile)

    if profile.level not in ["Speaker", "Master"]:
        messages.warning(request, "Certificate unlocks at Speaker level and above.")
        return redirect("learning:dashboard", profile_id=profile.id)

    badges = BadgeAward.objects.filter(learner=profile)
    context = {
        "profile": profile,
        "badges": badges,
    }
    return render(request, "learning/certificate.html", context)


