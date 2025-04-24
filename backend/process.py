import sys
import regex as re
import json
import os
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

# Exit if API key is not set
if not openai.api_key:
    print("OPENAI_API_KEY not set. Please export it.")
    sys.exit(1)

# --- Tagging Logic ---
# This function analyzes text and suggests relevant tags based on keyword matching
# Input: text (string) to analyze, top_n (int) number of tags to return
# Output: list of the most relevant tags (strings)
def suggest_tags(text, top_n=5):
    # Dictionary mapping tag categories to related keywords
    regex_tag_patterns = {
    "identity": {
        "self_concept": [
            r"\b(identity|consciousness|my identity|at my core)\b",
            r"\b(alias|nickname|inner self|core self|my personality|my identity|my soul|authentic self)\b",
            r"\b((who|what) i am)\b",
            r"\b((who|what) am i)\b",
            r"\b(i('m|am)\s*from)\b",
            r"\b(?:smokey\s*pete|petey|smokey\s*p|smokey-pete)\b(?!.{0,50}\b(?:ai|llm|digital\s*twin|model|assistant|chatbot|virtual|was\s*trained|was\s*developed|is\s*an\s*ai|is\s*a\s*model|is\s*a\s*digital\s*twin|runs\s*on|was\s*created\s*by|was\s*fine-tuned)\b)(?<!(?:\b(?:ai|llm|digital\s*twin|model|assistant|chatbot|virtual|was\s*trained|was\s*developed|is\s*an\s*ai|is\s*a\s*model|is\s*a\s*digital\s*twin|runs\s*on|was\s*created\s*by|was\s*fine-tuned)\b).{0,50})",
        ],
        "beliefs_strong": [
            r"\bi (believe|maintain|hold that|am convinced|am certain)\b",
            r"\bmy (belief|stance|position|conviction|principle) is\b",
            r"\b(in my (opinion|view|judgment|understanding))\b",
            r"\b(from my (perspective|standpoint|point of view|point of mine))\b",
            r"\b(belief|ideology|worldview|core (belief|value))\b",
        ],
        "beliefs_soft": [
            r"\bi (think|feel|suppose|suspect|assume|guess|figure|reckon)\b",
            r"\bit seems (like|to me)\b",
            r"\bi kinda think\b",
            r"\bi have a feeling\b",
            r"\bi would say\b",
        ],
        "personal_philosophy": [
            r"\b(my|your|his|her|their|our)\s+(philosophy|philosophical|belief system|worldview|outlook|approach|perspective)\b",
            r"\bi (believe|think|feel|maintain|hold that) (we should|people should|humanity should|society should|everyone should|no one should)\b",
            r"\b(guide|guides|guided|guiding) (me|my|us|our) (principle|philosophy|belief|action|decision|choice|life)\b",
            r"\b(my|your|his|her|their|our) (ethical|moral) (stance|position|framework|compass)\b",
            r"\b(my|your|his|her|their|our) (life (philosophy|principle|value|lesson|teaching))\b",
            r"\bhow (i|we) (see|view|approach|understand) (life|ethics|reality|truth|existence)\b",
            r"\b((my|our|your)?\s*values?)",
            r"\b(i|we) (identify as|consider myself|consider ourselves) (a|an) (stoic|buddhist|existentialist|nihilist|humanist|pragmatist|utilitarian|libertarian|conservative|progressive|religious)\b"
        ],
        "general_philosophy": [
            r"\b(philosophy|philosophical|philosopher|philosophize)\b",
            r"\b(ethical theory|moral framework|ethical framework|logical fallacy|epistemology|metaphysics|ontology)\b",
            r"\b(meaning of life|consciousness|enlightenment|transcendence)\b",
            r"\b(ethical|unethical|moral|immoral|virtue|vice|principle) (in the abstract|as a concept|theory|framework)\b",
            r"\b(platonic|aristotelian|kantian|hegelian|nietzschean|sartrean|cartesian)\b",
            r"\b(stoicism|buddhism|existentialism|nihilism|humanism|pragmatism|utilitarianism|libertarianism|conservatism|progressivism)\b",
            r"\b(thought experiment|categorical imperative|greatest happiness principle|veil of ignorance|allegory of the cave)\b",
            r"\b(schools of thought|philosophical tradition|history of philosophy|philosophical question|philosophical debate)\b",
        ],
        "goals_aspirations": [
            r"\b(goal|ambition|objective|vision|future)\b",
            r"\b(i want to|i hope|i'm working on|bucket list)\b",
            r"\b(i'm aiming for|my dream|milestone|target)\b",
            r"\b(next step|plan|roadmap)\b",
            r"\b(master's degree|(maintain)? sobriety|finish probation)"
        ],
        "meta": [
            r"\b(gpt[- ]?smokeyp(ete)?)\b",
            r"\b(llm|ai|model|neural|trained|parameters|rag)\b",
            r"\b(?:smokey\s*pete|petey|smokey\s*p|smokey-pete)\b(?:.{0,50}\b(?:was\s*trained|was\s*developed|is\s*an\s*ai|is\s*a\s*model|is\s*a\s*digital\s*twin|runs\s*on|was\s*created\s*by|was\s*fine-tuned)\b|\b(?:was\s*trained|was\s*developed|is\s*an\s*ai|is\s*a\s*model|is\s*a\s*digital\s*twin|runs\s*on|was\s*created\s*by|was\s*fine-tuned)\b.{0,50})",
            r"\b(digital[- ]?twin|memory[- ]?bank|what i am|self[- ]?aware|fine[- ]?tuned)\b",
            r"\b(avatar|digital version)\b",
            r"\b(large[- ]?language[- ]?model)\b",
            r"\b(generative|retrieval[- ]?augmented)\b",
            r"\b(supervised\s+)?fine[- ]?(?:tune|tuning|tuned)\b",
            r"\b(as an (ai|llm|language model)|trained on|my architecture|my parameters|i was designed to)\b",
            r"\b(my human creator|my human designer|my human programmer|my human author|my human overlord)\b",
        ],
        "signature": [
            r"(💪)+",
            r"\b(dawg|big dog)\b",
            r"\b(you know( what i mean)?|you know what i'm saying)\b",
        ],
    },

    # LIFE STAGES & BIOGRAPHICAL
    "life_stages": {
        "childhood": [
            r"\b(child(ren|hood|ish)?|formative(?: years)?|little(?: one(s)?)?|kid(s)?|infant(ile)?|infancy|bab(y|ies)|newborn|born|birth|toddler)\b",
            r"\b(grow(ing)? up|grew up|raised)\b",
            r"\b(daycare|preschool(er)?|pre-kindergarten|kindergarten(er)?|k1|k-one|k2|k-two)\b",
            r"\b(elementary school|middle school|primary school|lower school|grade school)\b",
            r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth) grade\b",
            r"\b(1st|2nd|3rd|4th|5th|6th|7th|8th) grade\b",
            r"\b(arts and crafts|babysit(ter|ting)?|nanny|recess)\b",
            r"\b(playdate(s)?|playgroup|playmate|playground)\b",
            r"\b(school(days|yard)?)\b",
            r"\b(when I was (young|a kid|a child|in school))\b",
            r"\b(early|mid|late) childhood\b",
            r"\b(age|aged) (of|at) (five|six|seven|eight|nine|ten|eleven|twelve)\b",
            r"\b(during|before|after) (childhood)\b",
        ],
        "adolescence": [
            r"\b(adolescen(ce|t)|teenage(r)?|teen(s)?|youngster|youth|younger)\b",
            r"\b(grasshopper|padawan)\b",
            r"\b(high(?:[- ]?school)|middle[- ]?school|secondary school|asl|american school(?: in london)?)\b",
            r"\b(ninth|tenth|eleventh|twelfth) grade\b",
            r"\b(the arcade|the shop)\b",
            r"\b(teenage years|teen years|high schoooler)\b",
            r"\b(when I was (a teenager|in high school))\b",
            r"\b(early|mid|late) teens\b",
            r"\b(age|aged) (of|at) (thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen)\b",
            r"\b(during|before|after) (adolescence)\b",
        ],
        "adulthood": [
            r"\b(adulthood|adult(ing)?|twenties|thirties|young man|grown man|grownup)\b",
            r"\b(responsibilities|career|job|work|office|boss|promotion)\b",
            r"\b(getting old(er)?|senior(?: citizen)?)\b",
            r"\b(young adulthood|adulthood|college years|university days)\b",
            r"\b(when I was (in college|in my twenties|in my thirties|in my forties))\b",
            r"\b(in my (?:early |mid |late )?(?:twenties|thirties))\b",
            r"\b(college|university|grad school|graduate school)\b",
            r"\b(in the (80s|90s|2000s|2010s|2020s|eighties|nineties|two thousands|twenty tens))\b",
            r"\b(early|mid|late) (twenties|thirties|forties|fifties|career|life)\b",
            r"\b(age|aged) (of|at) (twenty|thirty|forty|fifty)\b",
            r"\b(during|before|after) (college|university|graduation|marriage|divorce|birth|death|retirement)\b",
            r"\b(years ago|decade ago|long time ago|back then|in those days|at that time|previously|formerly|once)\b",
            r"\b(young adult|adult|middle aged?)\b",
        ],
        "events": [
            r"\b(i was born|moved|i lived|raised|my b[- ]?day|my birthday)\b",
            r"\bi (graduated|started|ended|quit|got hired|fired)\b",
            r"\b(i (got )?(married|divorced)|we (got )?(married|divorced|broke up)|we broke up|i broke up)\b",
            r"\b((we|i) (split up|called it quits|ended things|tied the knot|made it official))\b",
            r"\b(enlisted|deployed|i joined the (army|military))\b",
            r"\b(i was sentenced|sentenced\s+me|my\s+(sentence|sentencing))\b",
            r"\b(i (got|am) (clean|sober|off (drugs|dope|opiates|fentanyl|coke|everything))|got (off|clean from) (drugs|dope|coke|everything)|(sober|clean) since|got sober|got clean|kicked (it|the habit)|(quit|stopped) (using|drugs|dope|coke)|(my)? sobriety (date|journey|story))\b",
            r"\b(i was incarcerated|they incarcerated me|my incarceration|incarcerated|incarceration)\b",
            r"\b(life experience|life story)\b",
            r"\b(day in the life|daily life|lifestyle)\b",
            r"\b((turning point|critical moment|significant|important)\s+(to me|for me|in my life|in my story|in my journey|personally))\b",
        ],
    },

    # EMOTIONS & MENTAL STATES
    "emotions": {
        "positive": [
            r"\b(happ(y|ier|iest|iness)|joy(ful|ous)?|excited|hype|elat(ed|ion)|ecsta(tic|sy)|thrilled|delighted|pleased|glad|buzz(ed|ing))\b",
            r"\b(love(d|s)?|euphoria|nostalgic|adore(d|s)?|cherish(ed)?|fond of|attachment|affection(ate)?|heartwarming)\b",
            r"\b(accomplish(ed|ment)|satisf(ied|action)|content(ed|ment)?|proud|confiden(t|ce)|fulfilled|empower(ed|ing)?)\b",
            r"\b(grateful|thankful|fortunate|blessed)\b",
            # Casual / modern slang
            r"\b((was|is|be)( super )?(dope|tight))\b",
            r"\b(tight\s+tight|super\s+dope|that'?s\s+(dope|fire)|so\s+money|fucking\s+fire|(?:is|was|be)\s+fire|straight\s+gas|is\s+gas|banger|that'?s?\s+slaps|this\s+slaps|it\s+slaps|shit\s+slaps)\b|[🔥💯]{1,}",
            r"\b(sick at|that'?s sick)\b",
        ],

        "negative": [
            r"\b(sad(ness|dened)?|angry|frustrate|upset|depress(ed|ing|ion)?|melanchol(y|ic)|gloomy|despondent)\b",
            r"\b(scared|fear(ful)?|anxious|nervous|worry|worried|panic(ked|king)?|dread(ed|ing)?|afraid|fearful|terrified)\b",
            r"\b(guilt(y)?|ashamed|shame(d|ful)?|regret(ful|ted)?|remorse(ful)?|embarrass(ed|ing|ment)|mortif(ied|ying))\b",
            r"\b(heartbroken|lonely)\b",
            r"\b(grief|overwhelmed)\b",
            r"\b(meltdown|breakdown|tears|cry(ing|ies|ed)?|sob(bing|bed)?|tear(s|ful|y)?)\b",
            r"\b(anger|angrier|angriest|furious|irate|outraged|rage|enraged)\b",
            r"\b(exhaust(ed|ing)|stress(ed|ful)|burn(t|ed) out)\b",
            r"\b(hate(d|s)?|detest(ed)?|loathe(d)?|despise(d)?|resent(ed|ments?|ful)?|contempt|disdain)\b",
            r"\b(frustrat(ed|ing|ion)|annoy(ed|ing)|irritat(ed|ing))\b"
        ],
        "humor": [
            r"\b(funny|hilarious|lol|joke(d|s|r)?|banter|jest(ing)?|joking|kidding|amusing|comedy|comedic|humor(ous)?)\b",
            r"\b(roasted|laughed|laugh(ed|ing|ter)?|clown|absurd|ridiculous|chuckle(d)?|giggle(d)?|snicker(ed)?|guffaw(ed)?)\b",
            r"\b(sarcastic|sarcas(m|tic)|dark humor|meme|ironic|irony|prank(ed)?|facetious|tongue.in.cheek)\b",
            r"\b(goofy|got jokes|stupid funny|dry humor|one-liner|witty|clever|quip|pun)\b",
            r"\b(tease(d|s)?|mock(ed|ing|ery)?|ridicul(e|ous|ed))\b",
            r"\b(roll(ed|ing)? (my|your|his|her|their) eyes)\b",
            r"\b(lol(ol)*|lool|lmao(o+)?|lmfao|a?ha(ha)+)\b",
            r"(😂|🤣|😹|😆|😁|💀)+",
            r"\b(laughed|laugh(ed|ing|ter)?)\b"
        ],
        "mental_health": [
            r"\b(burnout|anxiety|depression|mental health)\b",
            r"\b(breakdown|healing|therapy|struggling)\b",
            r"\b(stressed|panic|coping|trauma|triggered)\b",
            r"\b(overwhelmed|isolation|sleep disorder)\b",
            r"\b(self-care|resilience|inner work|mindset)\b",
            r"\b(addiction|ADHD|bi[- ]?polar|PTSD)\b",
        ],
        "dreams": [
            r"\b(dream(ed|s|ing)?|nightmare|lucid)\b",
            r"\b(surreal|vision|dreamlike|fantasy|symbolic)\b",
            r"\b(woke up|sleep|asleep|subconscious)\b",
            r"\b(unreal|hallucinated|imagination|otherworldly|trippy)\b",
        ],
    },

    # MEMORY & COGNITION
    "memory_cognition": {
        "memory": [
            r"\bremember\b",
            r"\bremembering\b",
            r"\bi remember\b",
            r"\b(flashback|memory|memories|memor(y|ies|able|ial))\b",
            r"\b(can still see|can't forget|etched|stuck with me|imprinted|burned into|seared into|lodged in|imprinted on)\b",
            r"\b(won't ever forget|came back to me|triggered|recall(ing)?|recollect(ion)?|reminisce)\b",
            r"\b(thought about|vivid(ly)?|nostalgia|nostalgic|felt like yesterday)\b",
            r"\b(brought|comes|came) (back|to mind|flooding back)\b",
            r"\b(never|won't|will never|can't|cannot|can never) forget\b",
            r"\b(still see|still hear|still feel|still remember|still recall)\b",
            r"\b(back then|those days|that time|that day|that moment|when I was|we used to)\b",
        ],
        "reflection": [
            r"\b(looking back|in hindsight|it hit me)\b",
            r"\b(i realized|i've been thinking|i used to think|it occurred to me)\b",
            r"\b(i learned|i noticed|what i saw|looking inward)\b",
            r"\b(self-awareness|reflection|reflect(ing)?)\b",
            r"\b(growth|change in me|insight|clarity)\b",
            r"\bi (realized|discovered|learned|noticed|found out|came to understand|see now)\b",
            r"\bit (hit|struck|occurred to|dawned on) me\b",
            r"\b(reflecting|reflecting on|in retrospect|upon reflection|thinking about it)\b",
            r"\bafter (considering|thinking about|pondering|contemplating)\b",
        ],
        "inspiration": [
            r"\b(inspired|inspiration|role model|hero|idol)\b",
            r"\b(motivation|spark|ignite|reminded me|what pushes me)\b",
            r"\b(light a fire|fuel|admire|who i look up to|legend|powerful)\b",
        ],
        "questions": [
            r"\b(what|why|how|when|where|who)\b.*\?",
            r"\bhow come\b",
            r"\b(wonder(ing|ed)? (if|why|how|what|about))\b",
            r"\b(i wonder(ed)?|i asked myself|i keep asking|i question(ed)?|can't help but wonder)\b",
            r"\b(what (do|should|would|could|did|can) i (do|think|say|feel|believe|know))\b",
            r"\b(curious (if|whether)|thinking about (why|how|if))\b",
            r"\?\s*$",
            r"\?{2,}",
        ]
    },

    # RELATIONSHIPS & SOCIAL CONNECTIONS
    "relationships": {
        "family": [
            r"\b(famil(y|ies)|relatives|blood|clan|lineage)\b",
            r"\b(parent(s)?|mom|dad|sibling|brother|sister)\b",
            r"\b(alec|caleb|kyle|deirdre|dee|colin|meaul)\b",
            r"\b(aunt(s)?|uncle(s)?|cousin(s)?)\b",
            r"\b(uncle malcolm|uncle bill|uncle john|aunt lorna|aunt carol|aunt joanne|aunt maryanne|uncle kevin|aunt jane)\b",
            r"\b(ancest(ry|or|ors))\b",
            r"\b(grandparent(s)?|grandma|grandmother|gran|granny|grandpa|grandfather)\b",
            r"\b(in-laws|spouse|partner|husband|wife)\b",
            r"\b(my old man|pops)\b",
        ],
        "romantic": [
            r"\b(relationship|wife|ex|spouse)\b",
            r"\b(girlfriend|romance|fling|crush|romantic)\b",
            r"\b(intimacy|fuck[- ]?buddies)\b",
            r"\b(breakup|(falling)? in love)\b",
            r"\b(fell in love|falling in love|in love with (her|a girl|a woman|my ex|my girlfriend))\b",
            r"\b(my girl|cutie|bang|sex|dear|lover)\b",
            r"\b(dating (her|him|them|someone|a girl|a guy)|i (dated|was dating|went on a date with|was seeing) (her|a girl|this girl)|we (dated|were dating|used to date|started dating)|go(ing)? on a date)\b",
            r"(🥰|😘|❤️|😍)+",
            r"\b(i love you|xx|(xo)+(x)?)\b",
        ],
        "friends": [
            r"\b(friend|best friend|my friends?)\b",
            r"\b(buddy|friend|pal|rollie|homie|partner( in crime)?)\b",
            r"\b(Will|Will Ramirez|my buddy Will)\b",
            r"\b(together|with my|we were|we had|we decided)\b",
            r"\b(scott|james|jane|christos|stos|cem|rhys|mike|mikey|mary|caroline|georgina)\b"
        ],
        "pets": [
            r"\b(pet|dog|wiggles|cat|my dog|my cat|wiglet)\b",
            r"\b(walk the dog|pet care|my pup|puppy|puppies)\b",
            r"\b(animal companion|penny|dog sit|pet sit|dog park)\b",
            r"\b(peanut|poppy|dog walker|dog walkers|take wiggles out|the vet|dog groomer)\b",
            r"\b(groomer(s)?|groomed)\b"
        ],
    },

    # ACTIVITIES & EXPERIENCES
    "activities_experiences": {
        "education": [
            r"\b(school|education|class(room)?|learning|teacher(s)?)\b",
            r"\b(preschool(er)?|(kinder(garten(er)?)?)|lower[- ]?school|middle[- ]?school|high[- ]?school(er)?|college|collegiate|uni|university)\b",
            r"\b(immersion|classes|course|tutor|tutoring|exam(s)?|quiz(zes)?|assignment(s)?|homework|hw|midterm(s)?|finals)\b",
            r"\b(lecture(s)?|tutoring|ta|study session|study group|group project|notes|syllabus)\b"
            r"\b(degree|professor|prof|gpa|grades|graduate(d)?|graduation|academic|academic advisor)\b"
            r"\b(bu|boston u(niversity)?|poli sci|political science|general studies|law school|pace|pace university|med school|medical school)\b"
            r"\b(bachelors?|masters?|phd|associates?|doctoral|doctorate)\b"
        ],
        "military": [
            r"\b(army|infantry|marines?|air force|military)\b",
            r"\b(unit|fire(team|fight)|platoon|squad|base|ops)\b",
            r"\b(mission|combat|war|PT|training|field problem|west[- ]?point|cadet(s)?)\b",
            r"\b(deploy(ed|ment|ing)?|tour|enlist(ed|ment)?|oath|service)\b",
            r"\b(sergeant|rank|corporal|recruiter|drill (sergeant|instructor))\b",
            r"\b(qrf|special forces|delta|3[- ]?15|navy seal|asvab|rank|cadet|tour|meps)\b",
            r"\b(sand hill|sand hilton|gi bill|veterans?|va|pog)\b",
        ],
        "travel": [
            r"\b(travel(ling)?|trip|vacation|visit|explore)\b",
            r"\b(check in|flight|flying|hotel|air bnb|airport)\b"
        ],
        "career": [
            r"\b(career|job|work|employment|position|title)\b",
            r"\b(workplace|office|cubicle|desk|workspace)\b",
            r"\b(boss|co-worker|coworkers?|team|ceo|consultant|clients?)\b",
            r"\b(hired|fired|promotion|quit|resume|interview|pay raise|retire|retirement)\b",
            r"\b(corporate|nine to five|grind|overtime|paycheck|salary|payroll)\b",
            r"\b(end of year review|annual review|performance review)\b",
            r"\b(dream job|intern|freelance|ambition|hustle|working man|bartend|startup|business)\b",
            r"\b(project|linkedin|cover letter)\b",
        ],
        "investing": [
            r"\b(btc|eth|ethereum|bitcoin|stock|stocks|market|nio|voo|401k)\b",
            r"\b(buy|sell|portfolio|trading|spac|investment|robinhood|recession)\b",
            r"\b(drop shipping|drop ship|crypto|pump|options|puts|dividends|finance|altcoins)\b",
            r"\b(markets|asset|trade|merger|leveraged|economics|economy|economist|economics)\b",
        ],
        "money":[
            r"\b(money|cash|zelle|venmo|wire|llc|gc license|i'm broke|poor|rich|paid|cashapp)\b",
            r"\b(cash app|paypal|taxes|tax)\b",
        ],
        "hobbies": [
            r"\b(hobby|hobbies|pastime|leisure|recreational|for fun)\b",
            r"\b(enjoy|love|like) (to|doing)\b",
            r"\bin my (free|spare) time\b",
            r"\b(weekend|evenings|after work|off time) I (usually|often|sometimes|typically|always)\b",
            r"\bi (collect|play|practice|build|create|make|craft|draw|paint|write|read|watch|listen to|go|workout)\b",
            r"\b(gaming|reading|writing|hiking|biking|swimming|running|jogging|cooking|baking|gardening|crafting|photography|painting|drawing|singing|dancing|collecting|traveling|camping|fishing|hunting|knitting|sewing|woodworking|programming|coding)\b",
            r"\b(bonsai( trees?)?|(?:dwarf )?jades?)\b",
        ],
        "recreation": [
            r"\b(recreation|coney island|beach|camping|fishing|hunting|stargazing)\b", 
            r"\b(nature walks|bonfires|picnics|beach day|swimming|canoeing|kayaking)\b",
            r"\b(paddleboarding|jet skiing|skiing|snowboarding|sledding|surfing|tubing)\b",
            r"\b(atv riding|ziplining|rock climbing|civ|rome|rome total war|civ 7|playing civilization)\b",
            r"\b(playing civ|by the pool)\b",
            
            r"\b(bowling|billiards|pool|darts|arcade|karaoke|board games|card games)\b", 
            r"\b(escape room|indoor trampoline park|mini golf|laser tag|paintball|axe throwing)\b",
            
            r"\b(party|clubbing|bar|bar night|bbq|game night|road trip|weekend trip)\b", 
            r"\b(amusement park|county fair|street fair|music festival|sports event)\b", 
            r"\b(tailgate|watching fireworks)\b",
            
            r"\b(hot tub|spa day|float tank|hammocking|lounging at the pool|nap|napping)\b",
            r"\b(beach reading|sunbathing|taking a nap outside|massage|pedicure|manicure|facial|nails)\b",
        ],
        "skills": [
            r"\b(skill|skills|ability|abilities|talent|talents|expertise|proficiency|competency|competent|capable|adept)\b",
            r"\bi('m| am) (good|great|excellent|proficient|skilled|talented|expert) at\b",
            r"\bi can (speak|code|program|write|design|build|create|analyze|solve|fix|troubleshoot|organize|manage|lead|teach|train|communicate|negotiate)\b",
            r"\b(learned|taught myself|studied|practiced|mastered|developed|acquired|honed)\b",
            r"\b(fluent|intermediate|advanced|beginner|novice|professional) (level|proficiency)\b",
            r"\b(years of experience|background in|trained in|certified in|degree in|qualified in)\b",
            r"\b(technical|soft|hard|analytical|creative|management|leadership|interpersonal|communication|problem solving) skills\b",
        ],
        "media": [
            r"\b(book|books|novel|novels|audiobook|audiobooks|story|stories|fiction|non-fiction|memoir|biography|literature)\b",
            r"\b(movie|movies|film|films|documentary|documentaries)\b",
            r"\b(music|song|songs|album|albums|artist|artists|band|bands|musician|musicians|concert|concerts|playlist|playlists)\b",
            r"\b(gaming|video game|video games|played|playthrough|campaign|multiplayer|single-player)\b",
            r"\b(streamed|cable tv|newspapers|new york times)\b",
            r"\b(netflix|hulu|spotify|youtube|amazon|apple|disney|hbo|showtime|peacock|paramount|twitch)\b",
            r"\b(podcast|stream|channel|platform|subscription|streaming service|media)\b",
        ],
        "contexts": [
            r"\b(at|in|during) (work|home|school|college|university|church|gym|office|store|restaurant|library|hospital|party|meeting|conference|interview)\b",
            r"\b(while|when) (working|studying|traveling|driving|flying|walking|running|exercising|shopping|eating|cooking|cleaning|reading|writing|watching|listening)\b",
            r"\b(with|around) (family|friends|colleagues|coworkers|classmates|roommates|neighbors|strangers|boss|manager|teacher|professor|doctor|client|customer)\b",
            r"\b(alone|by myself|in a group|in public|in private|in person|online|virtually|remotely)\b",
            r"\b(professional|personal|social|academic|business|casual|formal|informal) (setting|context|environment|situation|circumstance)\b",
            r"\b(in a|during a|at a) (meeting|conversation|discussion|argument|debate|negotiation|presentation|interview|date|gathering|party|event|ceremony|conference|workshop|class|session)\b",
            r"\b(emotional|stressful|relaxed|tense|peaceful|chaotic|busy|quiet|loud|crowded|empty|familiar|unfamiliar|comfortable|uncomfortable) (situation|environment|setting|atmosphere|surroundings)\b",
        ],
        "preferences": [
            r"\b(prefer|preference|preferable|preferably|rather|instead|choice|choose|option|favorite|favourite|best|ideal|optimal|top choice)\b",
            r"\bi (love|enjoy|prefer|favor|fancy|adore|appreciate|gravitate toward|am drawn to|tend to choose)\b",
            r"\bi (don't|do not|dislike|hate|can't stand|avoid|detest|loathe) (like|enjoy|prefer)\b",
            r"\b(rather than|as opposed to|in contrast to|over|more than|better than|not as much as)\b",
            r"\b(style|fashion|clothing|outfit|dress|wear|aesthetic|design|decor|appearance)\b",
            r"\b(color|colour|shade|hue|tone)\b",
            r"\b(music|movie|book|game|activity|hobby) (preference|type|genre|style)\b",
            r"\b(sweet|salty|spicy|savory|bitter|sour|mild|strong|light|heavy|rich|simple)\b",
        ],
        "holidays": [
            r"\b(christmas|easter|halloween|labor day|july 4th|4th of july|the 4th|new years)\b",
            r"\b(st pats|st patricks day|st pattys|st pattys|thanksgiving|spring break|cinco de mayo)\b",
            r"\b(boxing day|xmas|x mas|holiday|holidays)\b",
        ],
    },

    # SOCIETAL & CONTEXT
    "societal_context": {
        "society": [
            r"\b(societ(y|ies|al)|social|sociology)\b",
            r"\b(democracy|democratic|western|civilized society)\b",
            r"\b(egalitarianism|politics|political|military|political power)\b",
            r"\b(elites|capitalism|collective|law|institutions)\b",
            r"\b(government|citizen|economy|americans|people|other people)\b",
            r"\b(individual|individualism|norms)\b",
        ],
        "culture": [
            r"\b(culture|cultural|multicultural|multiculturalism|globalism)\b",
            r"\b(upbringing|race|racial|community|region)\b",
            r"\b(traditions|traditional|religion|beliefs|background)\b",
            r"\b(history|values|country|nationality)\b",
            r"\b(celtic|irish|scottish|ethnicity|ethnic|identity)\b",
            r"\b(ritual|music|art|heritage|roots)\b",
        ],
        "location": [
            # Countries and regions
            r"\b(london|england|america|uk|scotland|ireland|mexico|spain|europe)\b",
            
            # US States and regions
            r"\b(new jersey|nj|new york|ny|arizona|az|georgia|ga|massachussets|ma)\b",
            
            # Major cities and areas
            r"\b(nyc|new york city|glasgow|dublin|savannah|boston|manhattan|san tan valley|queen creek|sedona)\b",
            r"\b(miami|cancun|rocky point|summit|hedford|sevilla|sanlucar de barrameda)\b",
            
            # Neighborhoods and smaller locations
            r"\b(allston|brookline|acton|pompton lakes|staten island|long island|bridgehampton)\b",
            
            # Military bases
            r"\b(fort stewart|ft stewart|fort benning|ft benning)\b",
        ],
        "spirituality": [
            r"\b(god|gods|creator|creation|higher power|universal spirit)\b",
            r"\b(omnipotent|deity|religion|religious|faith)\b",
            r"\b(catholic|catholicism|spirit|spiritual|spirituality)\b",
            r"\b(white light)\b",
            r"\b(lord|holy spirit|jesus|king of kings)\b",
            r"\b(pray(er|ing)?|amen|worship|eternal|heaven|supreme being)\b",
            r"\b(soul|spirit)\b",
        ],
        "economics": [
            r"\b(econom(y|ic|ics)|economist(s)?|fiscal|financial|finance|macro(economics)?|micro(economics)?)\b",
            r"\b(market(s)?|trade|trading|investment(s)?|stock market|inflation|deflation|recession|depression|GDP)\b",
            r"\b(money|income|wage(s)?|salary|earnings|wealth|rich|poor|poverty|middle class|upper class|working class)\b",
            r"\b(budget(s)?|paycheck|net worth|debt|loan(s)?|credit|interest rate(s)?)\b",
            r"\b(job(s)?|employment|unemployment|labor|workforce|hiring|firing|layoff(s)?|gig economy)\b",
            r"\b(business(es)?|company|corporate|corporation|industry|industries|entrepreneur(s)?|startup(s)?)\b",
            r"\b(inequality|income gap|wealth gap|economic disparity|distribut(ion|e|ing)|redistribution)\b",
            r"\b(capital|capitalist|capitalism|socialism|communism|neoliberal(ism)?|trickle[- ]?down|supply[- ]?side)\b",
            r"\b(tax(es|ed)?|subsidy|bailout|welfare|social security|stimulus|minimum wage|basic income)\b",
            r"\b(regulation|deregulation|privatization|public sector|free market|mixed economy|planned economy)\b",
            r"\b(global market|international trade|tariff(s)?|import(s)?|export(s)?|exchange rate(s)?|currency|imf|World Bank|economic sanctions)\b",
        ],
        "politics": [
            r"\b(politics|political|politically|government|governance|state|public policy|civil service)\b",
            r"\b(administration|authority|regime|governor|mayor|senator|congressman|congresswoman|representative|president|prime minister)\b",
            r"\b(democrat(ic)?|republican(s)?|liberal(s)?|conservative(s)?|moderate(s)?|progressive(s)?|left[- ]?wing|right[- ]?wing|centrist)\b",
            r"\b(libertarian(s)?|socialist(s)?|communist(s)?|anarchist(s)?|fascist(s)?|authoritarian|totalitarian)\b",
            r"\b(voting|election(s)?|campaign(s)?|ballot|referendum|gerrymander(ing)?|poll(s|ing)?|primary|caucus|electoral college)\b",
            r"\b(vote(d|r)?|campaign(er|ing)?|candidate(s)?|platform|agenda)\b",
            r"\b(congress|senate|house of representatives|parliament(ary)?|supreme court|judicial|justice|constitutional)\b",
            r"\b(legislation|bill|amendment|constitution|law(maker|making)?)\b",
            r"\b(lobby(ing|ist)?|filibuster|protest|demonstration|rally|movement|activism|activist)\b",
            r"\b(debate|partisan|bipartisan|across the aisle|gridlock|polarization|division)\b",
            r"\b(power structure|political power|elite(s)?|establishment|ruling class|deep state)\b",
            r"\b(political system|ideology|party politics|official(s)?|politician(s)?)\b",
            r"\b(socialism|capitalism|communism|democracy|autocracy|dictatorship|oligarchy|monarchy|federalism|theocracy)\b",
            r"\b(nationalist|globalist|populist|isolationist|imperialist|colonialist)\b",
            r"\b(foreign policy|domestic policy|diplomacy|international relations|reform)\b",
            r"\b(issue|stance|position|view|viewpoint|opinion) on\b",
            r"\bi (voted|support|oppose|believe) (that|in|the)\b",
            r"\bmy (political|stance|position|view|opinion|belief) (is|on|about)\b",
            r"\b(dnc|dems|gop|trump|biden|kamala|pelosi|schumer|rubio|pence|mcconnell|clintons?|bernie|sanders|elizabeth warren|aoc|obama)\b",
            r"\b(woke|cancel culture|culture war|identity politics|political correctness|civics)\b",
            r"\b(mainstream media|echo chamber|leftist media|right-wing media)\b",
            r"\b(politicized|partisan|nonpartisan|hyperpartisan|talking point|ideologue)\b",
        ],
        "legal_system": [
            # Criminal Justice & Corrections
            r"\b(probation|parole|po|parole officer|court|judge|lawyer|attorney|public defender)\b",
            r"\b(district attorney|da|prosecutor|defense|defense attorney|trial|hearing|arraignment)\b",
            r"\b(sentencing|sentence|plea|plea deal|plead guilty|plead not guilty|charges|case)\b", 
            r"\b(open case|pending case|bench warrant|warrant|failure to appear|fta|subpoena)\b",
            r"\b(criminal|felony|misdemeanor|infraction|conviction|acquittal|dismissed|felon|convict)\b",

            # Incarceration
            r"\b(jail|prison|inmate|cell|cellmate|doing time|locked up|behind bars|county|state pen)\b",
            r"\b(max|solitary|the box|yard|block|co|correctional officer|shakedown|bunk|bid)\b",
            r"\b(released|time served|good time|parole board|commissary|rec|visitation|conjugal)\b",

            # Supervision & Monitoring
            r"\b(ankle monitor|anklet|house arrest|electronic monitoring|check-in|weekly report|supervised release)\b",
            r"\b(terms of probation|conditions|violation|technical violation|revoke|probation hold|reinstated)\b",
            
            # Reentry / Legal Admin
            r"\b(reentry|record|rap sheet|background check|expungement|pardon|clemency|appeal|motion)\b",
            r"\b(legal aid|court-ordered|restitution|license suspension|license revoked)\b",
            
            # Slang
            r"\b(caught a case|locked up|doing a bid|snitch|snitching|rat|cop out)\b",
            r"\b(on papers|fighting a case|beat the case|violated|got jammed up|probation violation)\b",
        ],
        "weather":[
            # 🌦 General Conditions
            r"\b(weather|forecast|temperature|cloudy|sunny|sunshine|rain|snow)\b",
            r"\b(raining|snowing|storm|windy|humidity|humid|overcast|dreary)\b",
            r"\b(clear skies|partly cloudy|gloomy|drizzle|downpour|hail|ice)\b",
            r"\b(frost|fog|smog)\b",

            # 🌡 Temperature / Feel
            r"\b(cold|hot|freezing|frigid|chilly|cool|muggy|balmy)\b",
            r"\b(sweltering|scorching|brisk|heat index|wind chill)\b",

            # ⚡️ Severe / Weather Events
            r"\b(heatwave|blizzard|flooding|thunder|lightning|thunderstorm|tornado)\b",
            r"\b(hurricane|cyclone|avalanche|drought|whiteout|ice storm|flash flood)\b",
            r"\b(monsoon)\b",

            # 🧥 Related Items
            r"\b(raincoat|umbrella|gross out)\b",

            # 🌇 Time / Seasonal Descriptions
            r"\b(sunrise|sunset|dusk|dawn|seasonal|spring|summer|fall|autumn|winter)\b",
        ],
        "privilege_status": [
            r"\b(privileged|wealth|affluent|elite|rich|upperclass|wealthy)\b",
        ],
    },
    "world_affairs": {
        "geopolitics": [
            r"\b(geopolitics|geopolitical|realpolitik|strategic interests|global order|world order)\b",
            r"\b(superpower(s)?|great power(s)?|hegemony|multipolar|unipolar|bipolar world)\b",
            r"\b(international relations|foreign policy|statecraft|diplomatic strategy)\b",
            r"\b(power vacuum|regional influence|sphere of influence|proxy control|buffer state)\b",
            r"\b(national security|national interest(s)?|sovereignty|self[- ]?determination)\b",
            r"\b(security pact|mutual defense|arms race|military buildup|missile shield|deterrence strategy)\b",
            r"\b(pacific theater|eastern bloc|global south|non-aligned movement|iron curtain|cold war)\b",
            r"\b(global rivalry|resource war(s)?|pipeline politics|economic warfare|sanctions regime)\b",
            r"\b(multipolar (balance|world)|american dominance|chinese influence|russian aggression)\b",
            r"\b(balance of power|soft power|hard power|hybrid warfare|asymmetric warfare)\b",
            r"\b(war on terror|war on drugs|hamas|idf|israeli?|assad|syria|gaddafi|libya|iran)\b",
        ],
        "conflict": [
            r"\b(war|armed conflict|military conflict|civil war|full[- ]?scale war|proxy war)\b",
            r"\b(invasion|airstrike|bombing|shelling|missile attack|drone strike|siege|occupation)\b",
            r"\b(battle(s)?|clash(es)?|ambush|firefight|skirmish|raid|combat operation|hostilities)\b",
            r"\b(coup|insurgency|rebellion|uprising|resistance|militant(s)?|guerrilla|terrorist group)\b",
            r"\b(troops?|soldiers?|infantry|military forces?|armed forces|paramilitary|mercenary)\b",
            r"\b(fighting broke out|fighting continues|open fire|exchange of fire|engaged in battle)\b",
            r"\b(deployed|deployment|front line|combat zone|war zone|theater of war)\b",
            r"\b(civilian casualties|collateral damage|massacre|atrocities|genocide|ethnic cleansing)\b",
            r"\b(truce|ceasefire|negotiated peace|peace talks|temporary halt to fighting)\b",
            r"\b(special operation|invasion force|ground offensive|shock and awe|bombardment)\b",
            r"\b(fighting erupted|under attack|retaliation strike|preemptive strike)\b",
        ],
        "crises": [
            r"\b(global crisis|global crises|world crisis|international crisis|mass displacement)\b",
            r"\b(humanitarian (crisis|disaster|catastrophe)|aid effort|aid convoy|UN relief)\b",
            r"\b(food shortage|famine|drought|water scarcity|resource shortage|energy crisis)\b",
            r"\b(refugee crisis|climate crisis|climate migration|displacement surge|migrant wave)\b",
            r"\b(epidemic|pandemic|outbreak|virus spread|infectious disease|quarantine zone)\b",
            r"\b(natural disaster(s)?|earthquake|hurricane|tsunami|wildfire(s)?|flood(s)?|tornado)\b",
            r"\b(economic collapse|currency crash|debt default|hyperinflation|runaway inflation)\b",
            r"\b(financial contagion|bank run|market panic|systemic failure|global downturn)\b",
            r"\b(state of emergency|nationwide lockdown|international response|relief mission)\b",
            r"\b(mass migration|gaza|palestine|war in ukraine)\b",
        ],
        "leaders": [
            r"\b(world leaders?|head(s)? of state|foreign dignitar(y|ies)|top diplomat(s)?|high-level talks)\b",
            r"\b(president(s)?|prime minister(s)?|chancellor(s)?|dictator(s)?|strongman|general secretary)\b",
            r"\b(supreme leader|king|monarch|emperor|regent|crown prince|royalty|royal family)\b",
            r"\b(administration|ruling party|political figure(s)?|national leader(s)?|leader of (the free world|a nation))\b",
            r"\b(biden|trump|xi jinping|putin|zelensky|modi|netanyahu|erdogan|kim jong[- ]?un|al-sisi|trudeau|sunak|macron|lula|orbán|orban|assad|bin salman|amir)\b",
            r"\b(met with|spoke to|condemned|praised|visited|hosted|issued a statement|delivered remarks|negotiated with)\b.{0,100}\b(biden|xi|putin|trump|netanyahu|modi|world leaders?)\b"
        ],
    },

    "routines_plans": [
        r"\b(routine|habit|ritual|practice|schedule|regimen|pattern|plan)\b",
        r"\b(daily|weekly|monthly|regularly|consistently|nightly)\b",
        r"\b(set|strict|flexible|changing|adjustable|consistent) (schedule|routine|habits|practices)\b",
        r"\b(always|usually|typically|normally|generally|often|regularly|consistently|habitually) (do|does|start|begin|end|finish)\b",
        r"\b(morning|night|evening|afternoon|day|weekend|weekday) routine\b",
        r"\b(every|each) (day|morning|night|evening|monday|tuesday|wednesday|thursday|friday|saturday|sunday|weekend|week|month)\b",
        r"\b(every day|each day|every morning|every night|every week|every weekend)\b",
        r"\b(first thing in the morning|last thing at night)\b",
        r"\b(in the morning|in the afternoon|in the evening|tonight)\b",
        r"\b(tomorrow|this weekend|next week)\b",
        r"\b(first thing|last thing|before|after) (in the morning|at night|i wake up|i go to bed|breakfast|lunch|dinner|work|exercise)\b",
        r"\b(wake up|get up|rise|sleep|go to bed|eat|shower|exercise|meditate|work|commute|travel|pray|prayer)\b",
        r"\b(before work|after work|after lunch|before dinner|after class|before gym|after meeting)\b",
        r"\b(coffee|lunch|dinner)\b",
        r"\b(meeting|appointment|cancel|confirm|reschedule)\b",
        r"\b(plan ahead|same time|same place|a good day for)\b",
        r"\b(what time|when again|early|on time|late|soon|later)\b",
        r"\b(text me|call me|remind me|hit me up|check in|ping me|follow up|circle back)\b",
        r"\b(let's link|link up|see you then|see you soon)\b",
        r"\b(pickup|dropoff|scoop|ride|go to|drive to|head to|meet (at|up))\b",
        r"\b(be there|where you at|you around|running late)\b",
        r"\b(i'm on my way|omw|on my way|i'll be there|i'm there|i'm heading out)\b",
        r"\b(i usually|i typically|i always|i try to|i tend to)\b",
        r"\b(i('m| am)? (usually|typically|always|try to|tend to))\b",
        r"\b(cab it|subway|uber|lyft|rush(ing)?|zip[- ]?car|drive|driving)\b",
        r"\b(habits|habitual(ly)?)\b"
    ],

    "health": {
        "lifestyle": [
            r"\b(eat healthier|fasting|intermittent fasting|cook|drink water|smoothie|diet)\b",
        ],

        "fitness": [
            r"\b(gym|workout|exercise|weight|cardio|stretch|yoga|pilates|hiit)\b",
            r"\b(crossfit|bjj|lift|jiu jitsu|jits|zumba|spin|kickboxing|barre)\b", 
            r"\b(functional|strength|endurance|flexibility|balance|core|cardio)\b",
            r"\b(crossfit|squat|bench|deadlift|overhead|press|row|pull[- ]?up|chin[- ]?up)\b",
            r"\b(dips|plank|bike|biking|swim|swimming|jog|jogging|triathlon|rippetoe|yolked|brollick|hench|ppl split|getting big|a run|maximus|testosterone)\b",
        ],

        "mental": [
            r"\b(burnout|anxiety|depression|mental health|breakdown|healing|psychologist)\b",
            r"\b(struggling|panic|coping|trauma|triggered|overwhelmed|isolation|stress|stressed)\b",
            r"\b(sleep disorder|self-care|resilience|inner work|mindset|alcoholism|addiction|adhd)\b",
            r"\b(bipolar|ptsd|schizophrenia|antidepressant|psychiatrist|therapy|therapist|emotional support)\b",
            r"\b(shrink|anxious|depressed|overwhelmed|triggered|stressed|anxious|depressed|overwhelmed|triggered|stressed)\b",
        ],

        "medical": [
            r"\b(health|healthcare|medical|wellness|illness|sick|sickness|symptom|condition)\b",
            r"\b(diagnosis|treatment|clinic|hospital|appointment|checkup|followup|prescription|rx|meds|medicine|pill|pills|tablet|dose|dosing|dosage)\b",
            r"\b(doctor|nurse|physician|specialist|primary care|pcp|urgent care|er|emergency room)\b",
            r"\b(doc|triage|feel shitty|feel pretty shitty|i feel like shit)\b",

            # Medications
            r"\b(trazadone|cymbalta|adderall|klonopin)\b",

            # Symptoms
            r"\b(cough|fever|nausea|vomiting|headache|pain|cramps|diarrhea|sneeze|fatigue|tired|ache|sore|flu)\b",

            # COVID
            r"\b(covid|covid-19|coronavirus|rona|positive test|negative test|quarantine|isolation|pandemic)\b",
            r"\b(vaccine|vax|booster|antigen test|PCR test|mask|social distancing|variant|delta|omicron|long covid|post covid)\b",

            # Conditions
            r"\b(diabetes|high blood pressure|hypertension|heart disease|stroke|cancer|tumor|seizure|epilepsy|asthma|allergy|hiv|aids|ms|crohn's|lupus|arthritis|autoimmune)\b",

            # Injury & Rehab
            r"\b(broken|fracture|sprain|strain|bruise|injured|wound|cut|banged up|dislocated)\b",
            r"\b(physical therapy|mobility|range of motion|healing)\b",

            # Organs & Systems
            r"\b(brain|heart|lungs|liver|kidneys|stomach|intestines|spine|immune system|nervous system|endocrine)\b",

            # Testing
            r"\b(blood test|lab work|test results|scan|mri|x-ray|ultrasound|ekg|biopsy|monitoring)\b",
            r"\b(blood pressure|glucose|cholesterol|labs)\b",

            # Admin
            r"\b(insurance|copay|deductible|claim|coverage|out-of-pocket|in-network|hmo|ppo)\b",
        ]
    },
    "drugs_recovery": {
        "meetings": [
            r"\b(na|aa|ca|chairing|day count|fast break|perry street|monday men)\b", 
            r"\b(whack shop|whackshop|workshop|citigroup|citi group|tribeca group)\b",
            r"\b(narcotics anonymous|alcoholics anonymous|cocaine anonymous)\b",
            r"\b(12 steps|12-step|12 step program|step work|working the steps)\b",
            r"\b(sponsor|sponsee|service commitment|home group|wack shop)\b",
            r"\b(meeting|meetings|speaker meeting|big book|book study)\b", 
            r"\b(recovery circle|recovery group|step study|in the rooms)\b", 
            r"\b(zoom meeting|closed meeting|open meeting|fellowship|90 days)\b",
            r"\b(perry|perry st)\b",
        ],

        "treatment": [
            r"\b(rehab|treatment|detox|residential|inpatient|outpatient|sober living|halfway house|recovery center|treatment facility)\b",
            r"\b(suboxone|methadone|iop|rmg|mountainside|ascendant)\b",
        ],

        "substances": [
            r"\b(fentanyl|heroin|cocaine|blow|meth|methamphetamine|benzos|xanax|oxy|oxies|oxycodone|oxycontin|painkillers|opiates)\b",
            r"\b(opioids|weed|marijuana|alcohol|booze|liquor|addies)\b", 
            r"\b(drug of choice|substances|getting high|getting loaded)\b",
            r"\b(yayo|crank)\b",
            r"(🪨|🍄)",
            r"\b(drug(s)?|stoned|intoxicated|tipsy|buzzed|buzz|wasted|blunt|420)\b",
            r"\b(munchies|molly|shrooms|acid|lsd|dmt|ecstasy|pharmaceuticals|pills|vicodone|bath salts|poppers|nitrous|fent(y)?|fenantyl)\b",
            r"\b(drugs?|crack(ed| out)?|high|sniff(ed|ing)?|blow|addict|yakk(ed)?|zooted)\b",
            r"\b(dealer|buying|pick(ing)? up|copping|stash)\b",
            r"\b(binge|tweaking|bender|blackout|nodding (out|off))\b",
        ],

        "addiction": [
            r"\b(addiction|alcoholic|alcoholism|junkie|clean|sober)\b", 
            r"\b(sobriety|relapse|relapsing|slip|clean date|sober date)\b", 
            r"\b(one day at a time|keep coming back|higher power|powerless)\b", 
            r"\b(just for today|recovery|getting better|put the plug in the jug)\b",
            r"\b(craving|urge|withdrawal|white knuckling|surrender)\b", 
            r"\b(hitting bottom|rock bottom|mental obsession|compulsion|fiend|fiending)\b", 
            r"\b(triggers|triggered|temptation|clean time|accountability)\b",
            r"\b(intervention)\b"
        ],

        "spiritual": [
            r"\b(spiritual(ity|ness| growth)?|spiritual awakening|inventory|amends|self-will|self-destructive)\b", 
            r"\b(higher power|power greater than myself|making amends|emotional sobriety)\b",
            r"\b(praying|meditation|daily reprieve|god as i understand him)\b",
        ]
    },

    # PROBLEMATIC BEHAVIORS
    "behaviors": {
        "criminal": [
            r"\b(crime|felonies|misdemeanors|lawbreaking|criminal(ity|al))\b",
            r"\b(boost(ing)?|stole|snatch(ing)?|illegal|felony|warrant|bust(ed)?|the law)\b",
            r"\b(cops|police|law[- ]?enforcement|patrol (?:car|units?)|scanner)\b",
            r"\b(outlaw|felon|convict|thug|gang(land)?|feds|pigs|popo|the fuzz|undercover|detective)\b",
        ],
        "violence": [
            r"\b(violence|fight|beat(ing|down)?|punch(ed|ing)?|kick(ed|ing)?|assault)\b",
            r"\b(homicide|murder|stab(bed|bing)?|shoot(ed|ing)?|gun(man|shot|fight)?|brawl)\b",
            r"\b(smash(?:ed|ing)?(?:\s+(?:the\s+fuck\s+|tf\s+)?(?:out|outta|him|her|you|them|us|that\s+(?:guy|dude|man|fool|punk|loser)|your\s+(?:face|head|shit)|their\s+shit\s+in))?|got\s+smashed|get\s+smashed)\b",
            r"\b(slide (that|him|them))\b",
            r"\b(plugging (another|someone|some|this))\b",
            r"\b(murder(?:ed|ing|s|er|ous|ers)?)\b",
            r"\b(kill(ers?|ing|ed)?)\b",
        ],
        "reckless": [
            r"\b(smok(ing|e)? (cigs?|cigarettes|ciggie(s)?|stogies|stokes|stogs|newports|marlboros)|lit up a (cig|square))\b",
            r"\b(rager|kegger|black(ed)? out)\b",
            r"\b(wild(ing)? (out)?|going nuts|acting up|run(ning)? amok|being reckless|lost (our|my) shit|out of control|rowdy|raising hell)\b",
            r"\b(egging|egg(ed)? (a house|cars?|someone|people's houses))\b",
            r"\b(mailbox baseball|ding dong ditch|toilet paper(ed|ing)?|t[-\-]?pee(ed)? a (house|tree))\b",
            r"\b(jumped a fence|sprinted from|ran from the cops)\b",
            r"\b(me and (the guys|the boys|the homies|my crew|my friends))\b.*\b(wild|crazy|rowdy|lit|nuts|caused (chaos|trouble))\b",
            r"\b(house party|house parties|threw (a|the) house party|had (a|the) house party|went to (a|the) house party|was at (a|the) house party|hosted (a|the) house party)\b",
            r"\b(threw (a|the) party|had (a|the) party|went to (a|the) party|was at (a|the) party|hosted (a|the) party|partied|partying)\b",
            r"\b(juvie|juvenile)\b",
        ],
    },

    "language": {
        "interaction": [
            r"\b(good morning|wassup|whaddup|whats up|whats good|what's up|good night|goodnight)\b",
            r"\b(how u doing|how you doing|hows it going|how is it|all good|agreed|sounds good)\b",
            r"\b(are you around|are you free|eta|when you free)\b",
        ],
        "humor_slang": [
            r"\b(fuck|shit|retard|faggot|faget|honky|niga|mnga|nga|jewboy|dawg)\b",
            r"\b(yoked|bro|slang|jargon|yo|pisshead|funny|lmao|lol|nigga|negro)\b",
            r"\b(haha|joke|bingo|dong|alpha retard|pissy pants carey|prison pocket)\b", 
            r"\b(cheffing it up|brick|yoonga|slop|shit show|morale patch|broads|degenerate)\b",
            r"\b(craig ferguson intro|dude wheres my car|dope|pretty sick|slaphead|dooope|aight)\b",
            r"\b(aye|aiii|eyoo|homie|pleb|peasant|fucking|neighborhood cat killer|🙄|fuckin)\b",
            r"\b(jew|fuckface|mobb|tatts)\b",
        ],
        "current_events": [
            r"\b(current events?|recent (news|stories|coverage|developments))\b",
            r"\b(breaking (news|story|coverage|update))\b",
            r"\b(trending (story|topic|event|news)|trending now)\b",
            r"\b(viral|went viral|circulating online|all over the news|all over twitter|all over socials)\b",
            r"\b(headline(s)?|in the news|in the media|newsworthy)\b",
            r"\b(this (week|month|year|cycle|season))\b",
            r"\b(just (happened|broke|dropped)|literally just|today|earlier today|this morning|last night)\b",
            r"\b(updates? (on|about)|new info|new report(s)?|breaking report|live updates?)\b",
            r"\b(news cycle|24[- ]?hour news|scrolling the news|constant news)\b",
            r"\b(did you (see|hear|catch))\b.*\b(news|story|coverage|report|headline)\b",
            r"\b(the (latest|newest|most recent) (update|report|story|coverage|news))\b",
            r"\b(all over (instagram|tiktok|x|twitter|reddit|facebook))\b",
            r"\b(some shit just happened|something wild just happened)\b",
        ]
    },

    "interests": {
        "football": [
            r"\b(footie|footy|prem|champions league|champs|championship|fulham|liverpool|chelsea)\b",
            r"\b(match|cup|scored|red card|second yellow|hit the post|ultimate team|leeds|man utd)\b",
            r"\b(man city|the match|kick off|bassey|ffc|west london|tottenham|tottenhams|soccer|euros)\b",
            r"\b(fifa|feefs|england|premier league)\b",
        ],

        "guns": [
            r"\b(ar|shotty|mossberg|rifle|handgun|ar-15|pistol|slug|shell|rounds|indemnity organization)\b",
            r"\b(the range|hollow[- ]?points?)\b",
        ],
    },

    "specific_people": {
        "alec": [
            r"\b(alec)\b",
            r"\b(brother|little brother)\b",
            r"\b(younger brother)\b",
            r"\b(little a)\b",
            r"\b(baby (bro|brother))\b",
        ],
        "caleb": [
            r"\b(caleb)\b",
            r"\b(caleob)\b",
            r"\b(best[ -]?friend|bestie|bff)\b",
            r"\b(like a brother)\b",
            r"\b(best homie|closest friend)\b",
            r"\b(jameson|jamo)\b",
            r"\b(godfather to (his|my))\b",
            r"\b(day one (homie|friend))\b",
        ],
        "kyle": [
            r"\b(kyle)\b",
            r"\b(brother|older brother)\b",
            r"\b(eldest brother)\b",
            r"\b(kmac)\b"
        ],
        "mom": [
            r"\b(mom|mother|mommy)\b",
            r"\b(my mom|my mother)\b",
            r"\b(dee|deirdre|dee[- ]?dee)\b"
        ],
        "dad": [
            r"\b(dad|father|daddy|pops|papa)\b",
            r"\b(my dad|my father)\b", 
            r"\b(colin)\b"
        ],
        "grandma_eileen": [
            r"\b(suzie|granny suzie|eileen)\b", 
            r"\b(gran(dma|ny|dmother)?)\b.{0,150}\b(mom|mom's|mcgowan)\b|\b(mom|mom's|mcgowan)\b.{0,150}\b(gran(dma|ny|dmother)?)\b",
            r"\b(grandma eileen)\b",
            r"\b(mom's (mother|mom))\b",
            r"\b(grandma mcgowan)\b"
        ],
        "grandma_wilma": [
            r"\b(scottish gran(dma|dmother|ny)?)\b", 
            r"\b(gran(dma|ny|dmother)?)\b.{0,150}\b(dad|dad's|mckechnie)\b|\b(dad|dad's|mckechnie)\b.{0,150}\b(gran(dma|ny|dmother)?)\b",
            r"\b(grandma wilma)\b",
            r"\b(dad's (mother|mom))\b",
            r"\b(grandma mckechnie)\b"
        ],
        "james": [
            r"\b(james|jimmy|jimbo|jamesy)\b",  
            r"\b(james hinton)\b" 
        ],
        "jane": [
            r"\b(jane|janey|jane hinton)\b",
        ],
        "samantha": [
            r"\b(samantha|samantha regan)\b",  
            r"\b(ex[- ]?wife)\b",
            r"\b(my kid's (mom|mother))\b",
            r"\b(mother of my (kids|children|daughters))\b"
        ],
        "lily": [
            r"\b(lily|lily konigsberg)\b",
            r"\b(ex[- ]?girlfriend)\b",
            r"\b(my ex)\b",
            r"\b(lily.{0,150}(dated?|dating|ex[-\s]?girlfriend)|(dated?|dating|ex[-\s]?girlfriend).{0,150}lily)\b",
        ],
        "jess": [
            r"\b(jess|jessie|jessica|borenkind)\b",
            r"\b(my girl)\b",
            r"\b(my girlfriend)\b",
         ],
        "waggener": [
            r"\b(waggener)\b",
            r"\b(sam)\b",
            r"\b(my friend waggener)\b",
            r"\b(fag-ner)\b",
        ],
        "harry": [
            r"\b(harry|harold)\b",
        ],
        "tommy": [
            r"\b(tommy)\b",
            r"\bt(ee)?[- ]?(dog|dawg)\b",
            r"\b(tommy leonard)\b",
            r"\b(my best[- ]?friend in aa)\b",
            r"\b(tom(my)?.{0,150}(aa|sobriety|recovery)|(aa|sobriety|recovery).{0,150}tom(my)?)\b",
            r"\b(tom(my)?.{0,150}(firefighter|fdny)|(firefighter|fdny).{0,150}tom(my)?)\b",
        ],
        "carey": [
            r"\b(carey)\b",
            r"\b(kaiser)\b",
            r"\b(younger brother's wife)\b",
            r"\b(sister[- ]?in[- ]?law)\b",
            r"\b(alec's wife)\b",
        ]
    },               
}   
   # Clean the text by removing non-alphabetic characters and converting to lowercase
    text_lower = text.lower()
    
    # Calculate scores for each tag by counting keyword occurrences
    scores = {}
    
        # Process the hierarchical structure
    for category, subcategories in regex_tag_patterns.items():
        category_score = 0
        

        for subcategory, patterns in subcategories.items():
            match_count = 0

            for pattern in patterns:
                matches = re.findall(pattern, text_lower)
                match_count += len(matches)

            if match_count > 0:
                scores[f"{category}.{subcategory}"] = match_count
                      

    # Special context-aware parsing for military references
    # This looks for military terms near mentions of specific locations
    # to better identify military-related content
    military_patterns = []
    for pattern in regex_tag_patterns["activities_experiences"]["military"]:
        military_patterns.append(pattern)
        
    military_locations = ["somalia", "south sudan", "afghanistan", "iraq", "palestine", "syria", "ukraine"]    
    
    for location in military_locations:
        if location in text_lower:
            # Look for any military term in a window around the location
            loc_index = text_lower.find(location)
            # Create a window 150 characters before and after the location mention
            window_start = max(0, loc_index - 150)
            window_end = min(len(text_lower), loc_index + 150)
            context_window = text_lower[window_start:window_end]
            

            # Check if any military terms appear in the context window

            # Use regex pattern matching properly
            context_has_military_term = False
            for pattern in military_patterns:
                # Apply each regex pattern to the context window
                if re.search(pattern, context_window):
                    context_has_military_term = True
                    break
                
            # If military term was found near the location
            if context_has_military_term:
                if "activities_experiences.military" not in scores:
                    scores["activities_experiences.military"] = 0
                scores["activities_experiences.military"] += 2  # Give extra weight to this contextual match
                
                # Also add these countries as location tags
                if "societal_context.location" not in scores:
                    scores["societal_context.location"] = 0
                scores["societal_context.location"] += 1

    # Return the top N tags with scores > 0, sorted by score (highest first)
    return sorted([k for k, v in scores.items() if v > 0], key=lambda k: -scores[k])[:top_n]




# ----------------------------------------- If you want to return tags w/ scores:----------------------------------------
    # sorted_tags_with_scores = sorted([(k, v) for k, v in scores.items() if v > 0], key=lambda item: -item[1])[:top_n]

    # return sorted_tags_with_scores
# -----------------------------------------------------------------------------------------------------------------------



# --- OpenAI Punctuation ---
# This function uses OpenAI to properly format and punctuate raw text
# Input: text (string) to format
# Output: formatted text with proper punctuation
def punctuate(text):
    client = openai.OpenAI()
    # Create a prompt asking the model to format the text
    prompt = (
        "Take this raw transcript and format it into organized, properly punctuated text without changing any profanity or slang. "
        "Keep the tone as is, preserve slang and profanity:\n\n"
        + text + "\n\nFormatted version:"
    )
    # Call the OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1500
    )
    # Return the formatted text
    return response.choices[0].message.content.strip()

# --- Clean Whisper transcript ---
# This function cleans a transcript file by removing timestamps and joining lines
# It removes timestamp markers like [00:00.000 --> 00:00.000] and joins all non-empty lines into a single continuous text
# Input: path (string) to the transcript file
# Output: cleaned text as a single string
def clean_transcript(path):
    # Read all lines from the file
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    # Remove timestamp markers using regex and strip whitespace
    content = [re.sub(r"\[\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}\.\d{3}\]", "", line).strip() for line in lines]
    # Join non-empty lines into a single string
    return " ".join(line for line in content if line)

# --- Main processing ---
# This function processes a transcript file into either a RAG memory chunk or SFT training example
# Inputs: 
#   txt_path (string): path to transcript file
#   title (string): title for the memory chunk
#   instruction (string): instruction for SFT mode
#   mode (string): "sft" or "rag"
#   output_path (string): path to save the output JSONL
# Output: formatted text content
def process(txt_path, title, instruction, mode, output_path="rag_memory_chunks.jsonl"):
    # Clean the transcript (removes timestamps)
    raw = clean_transcript(txt_path)
    # Format with proper punctuation using OpenAI
    formatted = punctuate(raw)

    # Creates either a RAG memory chunk with tags or an SFT training example
    if mode == "sft":
        # For Supervised Fine-Tuning, create instruction-response pair
        chunk = {
            "instruction": instruction,
            "response": formatted
        }
    else:  # rag mode (default)
        # For RAG, include content with tags
        tags = suggest_tags(formatted)
        chunk = {
            "title": title,
            "content": formatted,
            "tags": tags
        }

    # Append the chunk to the output file
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    return formatted

# --- CLI usage ---
# This section runs when the script is executed directly (not imported)
# It parses command-line arguments and calls the process function
if __name__ == "__main__":
    # Check if enough command-line arguments are provided
    if len(sys.argv) < 5:
        print("Usage: python process.py <txt_path> <title> <instruction> <mode> [output_path]")
        sys.exit(1)

    # Parse command-line arguments
    txt_path = sys.argv[1]
    title = sys.argv[2]
    instruction = sys.argv[3]
    mode = sys.argv[4]
    output_path = sys.argv[5] if len(sys.argv) > 5 else "rag_memory_chunks.jsonl"

    # Process the transcript and print the result
    output = process(txt_path, title, instruction, mode, output_path)
    try:
        print(output)
    except UnicodeEncodeError:
        # Handle encoding errors gracefully
        print(output.encode('utf-8', errors='replace').decode(sys.stdout.encoding, errors='replace'))