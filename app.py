import streamlit as st
import spacy
import datetime as dt
import pandas as pd
import csv
import os
import plotly.express as px
from spellchecker import SpellChecker
from collections import Counter 
from HanTa import HanoverTagger as ht
import time



@st.cache_resource 
def load_model():
    model = 'de_core_news_md'
    # HanTa model file must be present in the working directory (or provide an absolute path)
    tagger = ht.HanoverTagger('morphmodel_ger.pgz')
    nlp = spacy.load(model)
    spell = SpellChecker(language='de')
    spell_en = SpellChecker(language='en')
    return nlp, tagger, spell, spell_en
#Returning - nlp, tagger, spelling checker, spelling checker (english)

# ----------------------------------------------------------------------------
# Basic Features
# ----------------------------------------------------------------------------

#Getting - Text, Model
def basic_features(text, nlp):
    doc = nlp(text)
    
    word = [token for token in doc if not token.is_punct]
    sentence = list(doc.sents)
    
    word_count = len(word)
    sentence_count = len(sentence)
    average_word_per_sentence = word_count/sentence_count
    
    content_pos = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}
    content_words =[t for t in word if t.pos_ in content_pos]
    content_ratio = len(content_words)/word_count
    

    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'average_word_per_sentence': round(average_word_per_sentence,2),
        'content_ratio': round(content_ratio, 2),
    }
#Returning - dict with word_count, sentence_count, average_word_per_sentence, content_ratio


# ----------------------------------------------------------------------------
# Major Features
# ----------------------------------------------------------------------------

def tokenize(text, nlp):
    return nlp(text)

#Getting - Text, Model
def lexical_diversity_score(doc):
    words_list = [token for token in doc if not token.is_punct and not token.is_space]
    sentence = list(doc.sents)
    unique_words = len(set([t.lemma_.lower() for t in words_list]))
    word_count = len(words_list)
    content_pos = {"NOUN", "VERB", "ADJ", "ADV", "PROPN"}
    content_words =[t for t in words_list if t.pos_ in content_pos]
    content_ratio = len(content_words) / max(word_count, 1)
    lexical_diversity = unique_words / max(word_count, 1)
    return words_list, lexical_diversity
#Returning - Words List, Lexical Density

def lemma_conversion(doc):
    lemmas = [t.lemma_.lower() for t in doc 
          if not t.is_punct 
          and not t.is_space       
          and t.is_alpha]
    return lemmas


def mtld(lemmas, threshold=0.72):
    def mtld_pass(tokens):
        factor = 0
        ttr = 1.0
        types = set()
        tokens_in_factor = 0
        
        for token in tokens:
            types.add(token)
            tokens_in_factor += 1
            ttr = len(types) / tokens_in_factor
            
            if ttr <= threshold:
                factor += 1
                types = set()
                tokens_in_factor = 0
        
        if tokens_in_factor > 0:
            factor += (1 - ttr) / (1 - threshold)
        
        if factor > 0:
            return len(tokens) / factor 
        else:
            return 0
    
    forward = mtld_pass(lemmas)
    backward = mtld_pass(list(reversed(lemmas)))
    return round((forward + backward) / 2, 2)


# REPITITION DENSITY

#with stop words
def repetition_with_stop(tokenization):
    main_text = [token.lemma_.lower() for token in tokenization if not token.is_punct and not token.is_space and token.is_alpha]
    total_words = len(main_text)
    
    word_freq = Counter(main_text)
    
    threshold = max(2, round(total_words * 0.03))
    repeated_tokens = sum(count for count in word_freq.values() if count >= threshold)
    density = repeated_tokens / total_words
    
    return round(density*100,2)

#without stop words
def repetition_without_stop(tokenization):
    main_text = [token.lemma_.lower() for token in tokenization if not token.is_punct and not token.is_space and token.is_alpha and not token.is_stop]
    total_words = len(main_text)
    
    word_freq = Counter(main_text)
    threshold = max(2, round(total_words * 0.03))

    top_repeated = [(word, count) for word, count in word_freq.most_common(5) if count >= threshold]
    if top_repeated:
        df = pd.DataFrame(top_repeated, columns=['Word', 'Count'])
        st.dataframe(df)

    repeated_tokens = sum(count for count in word_freq.values() if count >= threshold)
    density = repeated_tokens / total_words
    return round(density*100,2)



def clause_density(tokenization, verbose = False):
    subordinate_clause_found = 0
    subordinate_clauses = set()
    relative_clause_found = 0
    relative_clauses = set()
    conjunctions = set()
    
    target_conjunctions = {
        "A1": {"und", "aber", "oder", "dann", "auch"},
        "A2": {"weil", "dass", "wenn"},
        "B1": {"obwohl", "ob", "als", "während", "bevor", "nachdem", "damit"},
        "B2": {"sodass", "indem", "falls", "sofern", "wobei", "weshalb"},
        "C1": {"wohingegen", "insofern", "gleichwohl", "wenngleich"}
    }

    CLAUSE_DEPS = {
        'oc',   # object clause (dass, ob)
        'rc',   # relative clause
        'advcl', # adverbial clause (weil, obwohl, wenn, damit)
        'acl',  # adjectival clause
        'ccomp', # clausal complement
        'xcomp', # open clausal complement
    }
    
    for sent in tokenization.sents:
        for word in sent:
            if word.dep_ in CLAUSE_DEPS:
                if word.dep_ in ('oc', 'ccomp', 'xcomp', 'acl'):
                    subordinate_clause_found += 1
                    subordinate_clauses.add(word)
                elif word.dep_ == 'rc':
                    relative_clause_found += 1
                    relative_clauses.add(word)
                elif word.dep_ == 'advcl':
                    subordinate_clause_found += 1  # adverbial = subordinate
                    subordinate_clauses.add(word)
    
    CEFR = 'B1'
    missing_words = target_conjunctions[CEFR] - conjunctions

    
    if verbose:
        print(f'Subordinate Clauses Found: {subordinate_clause_found}')
        print(f'Relative Clauses Found: {relative_clause_found}')
        print(f'Conjunctions Used: {conjunctions}')
        print(f'\nWriters of your level often use these conjunctions which you did not use')
        print(missing_words)

    total_clause_found = subordinate_clause_found + relative_clause_found
    return total_clause_found


# ----------------------------------------------------------------------------
# Error Finding
# ----------------------------------------------------------------------------

#SUBORDINATE CLAUSE ERROR

def subordinate_accuracy(tokenization, verbose=False):

    known_conjunctions = {"weil","dass","obwohl","wenn","ob","damit","bevor","nachdem"}

    correct = 0
    wrong = 0

    for sent in tokenization.sents:

        conj_tokens = [t for t in sent if t.text.lower() in known_conjunctions]
        if not conj_tokens:
            continue

        conj = conj_tokens[0]
        clause_heads = [t for t in sent if t.i > conj.i and not t.is_punct]
        if not clause_heads:
            continue

        head = max(clause_heads, key=lambda w: len(list(w.subtree)))

        clause_tokens = [t for t in head.subtree if not t.is_punct]

        verbs = [t for t in clause_tokens if t.pos_ in {"VERB","AUX"}]

        if not verbs:
            continue

        last_token = clause_tokens[-1]

        if last_token in verbs:
            correct += 1
        else:
            wrong += 1

    if verbose:
        total = correct + wrong
        print(f"Total Clauses: {total}")
        print(f"Correct: {correct}")
        print(f"Wrong: {wrong}")
        if total:
            print(f"Accuracy: {round(correct/total*100,2)}%")

    return wrong, correct + wrong
#Returning - sub_error_count (wrong), clause_count (total)



# ARTICLE ERROR

def article_error(doc, verbose=False):
    article_errors = 0
    gender_mapping = {
        'Masc' : 'der',
        'Fem': 'die',
        'Neut': 'das'
    }

    gender_override = {
        'Ball': 'Masc',
        'Mädchen': 'Neut',
        'Auto': 'Neut',
    }
    
    errors_found = False

    for sent in doc.sents:
        for token in sent:
            if token.pos_ == 'DET' and token.dep_ == 'nk':
                noun = token.head
                if noun.pos_ not in ('NOUN', 'PROPN'):
                    continue

                token_gender = token.morph.get('Gender')

                if noun.text in gender_override:
                    noun_gender = [gender_override[noun.text]]
                else:
                    noun_gender = noun.morph.get('Gender')
    
                if not token_gender or not noun_gender:
                    continue

                if token_gender != noun_gender:
                    errors_found = True
                    article_errors += 1
                    if verbose:
                        st.error(f"❌ Incorrect Gender for '{noun}' ({gender_mapping.get(token_gender[0], token_gender[0])})\n"
                                 f"You used '{token}': Correct Article Form: {gender_mapping.get(noun_gender[0], noun_gender[0])}")
                else:
                    if verbose:
                        st.success(f"✅ '{token} {noun}': Gender Agreement Correct")

    return article_errors


#VERB MORPHOLOGY

def verb_morphology(tokenization, verbose=False):
    modal_lemmas = {"können", "dürfen", "mögen", "müssen", "sollen", "wollen", "möchten",
                    "kann", "darf", "mag", "muss", "soll", "will", "werden"}
    haben_sein = {"haben", "sein"}
    werden = {"werden"}

    verb_errors = 0
    for sent in tokenization.sents:
        for token in sent:
            if token.pos_ == 'AUX' or token.lemma_.lower() in modal_lemmas:
                for child in token.children:
                    if child.dep_ in ('oc', 'pd'):
                        if not child.morph.get('VerbForm'):
                            continue
                        is_correct = False
                        if token.lemma_ in haben_sein:
                            is_correct = 'Part' in child.morph.get('VerbForm')
                        elif token.lemma_ in werden:
                            is_correct = 'Inf' in child.morph.get('VerbForm')
                        elif token.lemma_.lower() in modal_lemmas:
                            is_correct = 'Inf' in child.morph.get('VerbForm')
    
                        if is_correct:
                            if verbose:
                                st.success(f'✅ Correct: {token.text} + {child.text}')
                        else:
                            verb_errors += 1
                            if verbose:
                                st.error(f'❌ Error: {token.text} + {child.text}')
                        
    return verb_errors


# CASE ERRORS
 
clause_starters = {'weil', 'dass', 'ob', 'wenn', 'als', 'wer', 'welche', 
               'welcher', 'welches', 'obwohl', 'damit', 'bevor', 'nachdem'}
nom_pronouns = {
    "ich", "du", "er", "sie", "es", "wir", "ihr",
}
acc_pronouns = {
    "mich", "dich", "ihn", "sie", "es", "uns", "euch"
}
dat_pronouns = {
    "mir", "dir", "ihm", "ihr", "uns", "euch", "ihnen"
}

def case_error(text, tagger, nlp_model, verbose=False):
    case_errors = 0
    doc = nlp_model(text)
    
    for sent in doc.sents:
        tokens = [token.text for token in sent if token.text.strip()]
        if not tokens:
            continue
        
        tags = tagger.tag_sent(tokens)
        
        # split tags into clauses at clause boundary words
        clauses = []
        current_clause = []
        for tag in tags:
            word = tag[0]
            if word.lower() in clause_starters and current_clause:
                clauses.append(current_clause)
                current_clause = [tag]
            else:
                current_clause.append(tag)
        if current_clause:
            clauses.append(current_clause)
        
        # apply heuristic per clause independently
        for clause in clauses:
            pronouns_in_clause = [(i, word, pos) for i, (word, lemma, pos)
                                  in enumerate(clause) if word.lower() in
                                  nom_pronouns | acc_pronouns | dat_pronouns]
            
            for i, (idx, word, pos) in enumerate(pronouns_in_clause):
                t = word.lower()
                is_first_pronoun = (i == 0)
                
                if is_first_pronoun:
                    if t in acc_pronouns and t not in nom_pronouns:
                        case_errors += 1
                        if verbose:
                            st.error(f'❌ Wrong case: "{word}" is accusative but used as subject ({sent.text.strip()})')
                    elif t in dat_pronouns and t not in nom_pronouns:
                        case_errors += 1
                        if verbose:
                            st.error(f'❌ Wrong case: "{word}" is dative but used as subject ({sent.text.strip()})')
                    else:
                        if verbose:
                            st.success(f'✅ Correct: "{word}" ({sent.text.strip()})')
                else:
                    if t in nom_pronouns and t not in acc_pronouns and t not in dat_pronouns:
                        case_errors += 1
                        if verbose:
                            st.error(f'❌ Wrong case: "{word}" is nominative but used as object ({sent.text.strip()})')
                    else:
                        if verbose:
                            st.success(f'✅ Correct: "{word}" ({sent.text.strip()})')
                    
    return case_errors
#Returning - case_errors (int)


# PREPOSITION ERROR DETECTION

# Here the case detection is unreliable for nouns without definite articles. Works best with der/die/das/dem/den
# this is a Model limitation, not a logical limitation

dative_preps = {"mit", "von", "zu", "bei", "nach", "seit", "aus", "gegenüber"}
accusative_preps = {"durch", "für", "gegen", "ohne", "um"}

def preposition_errors(tokenization, verbose=False):
    prep_errors = 0
    for sent in tokenization.sents:
        for token in sent:
            if token.pos_ == 'ADP':
                for child in token.children:
                    if child.dep_ in ("nk", "obj", "ag"):
                        actual_case = child.morph.get('Case')
                        if not actual_case:
                            continue
                        if token.lemma_.lower() in dative_preps:
                            is_correct = 'Dat' in actual_case
                        elif token.lemma_.lower() in accusative_preps:
                            is_correct = 'Acc' in actual_case
                        else:
                            continue 

                        if is_correct:
                            if verbose:
                                st.success(f'✅ Correct: {token.text} + {child.text}')
                        else:
                            prep_errors += 1
                            if verbose:
                                st.error(f'❌ Error: {token.text} + {child.text}')
                        
    return prep_errors

# CAPITALIZATION ERROR

def cap_error(tokenization, verbose=False):
    cap_errors = 0
    for sent in tokenization.sents:
        for i, token in enumerate(sent):

            if not token.is_alpha:
                continue
                
            string = token.text
            
            if token.pos_ == ('NOUN'):
                if string.islower():
                    if verbose == True:
                        st.error(f"You did not capitalize {string[0]} in the Noun '{string.capitalize()}'")
                    cap_errors += 1

            elif token.pos_ == ('PROPN'):
                if string.islower():
                    if verbose == True:
                        st.error(f"You did not capitalize {string[0]} in the Proper Noun {string.capitalize()}")
                    cap_errors += 1
                    
            elif i == 0:
                if string.islower():
                    if verbose == True:
                        st.error(f"You did not capitalize the first letter of the sentence: {string[0]} ({string.capitalize()})")
                    cap_errors += 1
                
                
    return cap_errors



# SEPLLING CHECKER

def spell_check(tokenization, spell, spell_en):
    words_list = [token.lower_ for token in tokenization if not token.is_punct and not token.is_space]
    misspelled = {word for word in spell.unknown(words_list) if not spell_en.word_frequency[word.lower()]}

    spelling_error_count = len(misspelled)
    return misspelled, spelling_error_count


def v2_order(doc, text, verbose = False):
    all_pronouns = [
        # personal pronouns - nominative
        'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr',
        
        # personal pronouns - accusative
        'mich', 'dich', 'ihn', 'uns', 'euch',
        
        # personal pronouns - dative
        'mir', 'dir', 'ihm', 'ihnen'
    ]
    v2_errors = 0
    # Evaluate verb-second order per sentence (more reliable than splitting by newline)
    for sent in doc.sents:
        tokens = [t for t in sent if not t.is_punct and not t.is_space]
    
        known_conjunctions = {"weil","dass","obwohl","wenn","ob","damit","bevor","nachdem"}
    
    
        #if the sentence is empty this will skip that
        if not tokens:
            continue
    
        first_token = tokens[0].text.lower()
        
        if first_token in known_conjunctions:
            continue
    
        pronoun_index = None
        verb_index = None
    
        for i, t in enumerate(tokens):
            if (t.text.lower() in all_pronouns) and pronoun_index is None:
                pronoun_index = i
                pronoun = t
    
            if (t.pos_ in ('VERB', 'AUX')) and ('Fin' in t.morph.get("VerbForm")) and (verb_index is None):
                verb_index = i
                verb = t
                
    
        if pronoun_index is not None and verb_index is not None:
            if pronoun_index < verb_index and pronoun_index > 0:
                v2_errors += 1
                if verbose:
                    print(f'\nVerb Order Error: {pronoun} {verb}')
                    print(sent.text.strip())
    return v2_errors


# ----------------------------------------------------------------------------
# Error Finding
# ----------------------------------------------------------------------------

def errors_count(total, article_errors, verb_errors, case_errors, cap_errors, prep_errors, v2_errors):
    sub_error_count = total
    article_error_count = article_errors
    verb_error_count = verb_errors
    case_error_count = case_errors
    cap_error_count = cap_errors
    prep_error_count = prep_errors
    v2_error_count = v2_errors

    # Return order matches unpacking in Streamlit section below
    return sub_error_count, article_error_count, verb_error_count, case_error_count, cap_error_count, prep_error_count, v2_error_count


#ERROR RATE

def error_rate(word_count, article_error_count, verb_error_count, sub_error_count, prep_error_count, case_error_count, cap_error_count, v2_error_count):
    total_errors = article_error_count + verb_error_count + sub_error_count + prep_error_count + case_error_count + cap_error_count + v2_error_count

    return (total_errors / max(word_count, 1)) * 100


# ----------------------------------------------------------------------------
# Progress Modeling
# ----------------------------------------------------------------------------

def normalization(tokenization, mtld, avg_length, clause_density, sub_error_count, word_count, text):
    length_factor = min(1.0, word_count / 200)
    mtld_norm = min(mtld / 150, 1.0) * length_factor
    sent_norm = min(avg_length / 20, 1.0)

    subordinate_count = total_clause_found  

    effective_subordinate = max(subordinate_count - (sub_error_count * 0.8), 0)

    clause_density_ratio = effective_subordinate / word_count

    adj_clause_norm = min(clause_density_ratio / 0.10, 1.0)

    # Nominalization density
    nominalization_suffixes = (
        "ung","heit","keit","schaft","nis","tum","tion","ität",
        "ise","ize","arbeit","unft","ismus","ment","ance","ence"
    )

    def nominalization_density(tokenization):
        nouns = [t for t in tokenization if t.pos_ == "NOUN" and t.lemma_.lower().endswith(nominalization_suffixes)]
        wc = len([t for t in tokenization if not t.is_punct and not t.is_space])
        return len(nouns) / max(wc, 1)

    nomin_norm = min(nominalization_density(tokenization) / 0.04, 1.0)

    max_depth = max((len(list(token.ancestors)) for token in tokenization), default=0)
    dep_norm = min(max_depth / 10, 1.0)

    tier1_markers = {
        # basic coordination / contrast
        "aber","doch","und","oder","denn",
        
        # causal / reason
        "weil","da","deshalb","darum","daher","somit",
        
        # condition / time
        "wenn","falls","als","bevor","nachdem","während",
        
        # concession (basic)
        "obwohl","trotzdem"
    }

    tier2_markers = {
    # contrast framing
        "jedoch","allerdings","hingegen","dagegen","dennoch",
        "einerseits","andererseits","zwar",
        
        # addition
        "außerdem","zudem","darüber hinaus","ferner","weiterhin",
        
        # cause/result (more formal)
        "folglich","infolgedessen","demzufolge",
        
        # emphasis
        "insbesondere","vor allem","hauptsächlich",
        
        # sequencing
        "erstens","zweitens","drittens","schließlich","letztlich"
    }

    tier3_markers = {
        # framing
        "im hinblick auf",
        "vor dem hintergrund",
        "unter berücksichtigung",
        "im rahmen",
        "im kontext",
        "in anbetracht",
        
        # stance / evaluation
        "es lässt sich argumentieren",
        "es erscheint",
        "es ist anzunehmen",
        "es ist zu beachten",
        "es ist hervorzuheben",
        "es ist fraglich",
        "es ist umstritten",
        
        # reformulation
        "mit anderen worten",
        "anders ausgedrückt",
        "präziser formuliert",
        
        # concessive sophistication
        "nichtsdestotrotz",
        "wenngleich",
        "obgleich",
        
        # qualification
        "bis zu einem gewissen grad",
        "in gewisser weise",
        "gegebenenfalls",
        
        # structural reference
        "resultierend",
        "maßgeblich"
    }

    text_lower = text.lower()

    tier1_count = sum(1 for m in tier1_markers if m in text_lower)
    tier2_count = sum(1 for m in tier2_markers if m in text_lower)
    tier3_count = sum(1 for m in tier3_markers if m in text_lower)

    discourse_score = (
        tier1_count * 0.2 +
        tier2_count * 0.6 +
        tier3_count * 1.0
    )

    discourse_norm = min(discourse_score / 4, 1.0)
    
    return mtld_norm, adj_clause_norm, sent_norm, nomin_norm, dep_norm, discourse_norm


#LCI

def lci(
    word_count,
    mtld_norm,
    adj_clause_norm,
    sent_norm,
    nomin_norm,
    dep_norm,
    discourse_norm,
    sub_error_count,
    verb_error_count,
    case_error_count,
    prep_error_count,
    article_error_count,
    cap_error_count,
    spelling_error_count,
):
    complexity = (
    0.22 * mtld_norm        # lexical diversity
    + 0.16 * adj_clause_norm
    + 0.08 * sent_norm
    + 0.15 * nomin_norm     # dominant C1 driver
    + 0.08 * dep_norm
    + 0.20 * discourse_norm
)
    weighted_errors = (
        sub_error_count * 3.0
        + verb_error_count * 2.5
        + case_error_count * 2.0
        + prep_error_count * 1.5
        + article_error_count * 1.0
        + cap_error_count * 0.3
        + spelling_error_count * 0.3
    )

    grammar = max(0.0, 1 - (weighted_errors / max(word_count, 1)))
    grammar = grammar ** 1.5

    return complexity * grammar


#CEFR Level Prediction

def cefr(LCI):
    if LCI < 0.12:
        return ('A1')
    elif LCI < 0.38:
        return ('A2')
    elif LCI < 0.50:
        return ('B1')
    elif LCI < 0.60:
        return ('B2')
    elif LCI < 0.78:
        return ('C1')
    else:
        return ('C2')


#--------------------------------------------------------------------------------
# STREAMLIT CODE
#--------------------------------------------------------------------------------

st.set_page_config(layout="wide")
st.markdown("""
<style>
/* Main background */
.stApp {
    background-color: #222831;
    color: #F3F4F4;
}

/* Main text */
body {
    background-color: #393E46;
    color: #F3F4F4;
}

/* Buttons */
.stButton>button {
    background-color: #00ADB5;
    color: #F3F4F4;
    border-radius: 10px;
    border: none;
}

/* Button hover */
.stButton>button:hover {
    background-color: #EEEEEE;
    color: #393E46
}

/* Text area */
textarea {
    background-color: #393E46 !important;
    color: #F3F4F4 !important;
    border: 3px solid #00ADB5 !important;
    border-radius: 10px !important;
}

/* Text inputs + dropdowns */
input,
select {
    background-color: #2C2C2C !important;
    color: #F3F4F4 !important;
    border: 1px solid #EEEEEE !important;
    border-radius: 10px !important;
}

input::placeholder {
    color: #EEEEEE !important;
    opacity: 0.75;
}

textarea:focus {
    border-color: #EEEEEE !important;
    outline: none;
}

</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <h1 style='
        color:#00ADB5;
        font-size:42px;
        font-weight:700;
        margin-bottom:10px;
        text_align: center
    '>
    LexiTrack
    </h1>
    """,
    unsafe_allow_html=True
)

text = st.text_area('Enter your essay')

if not text.strip():
    button = st.button("Analyze")
    st.info("Type or paste an essay above to begin analysis")
    st.stop()

else:
    button = st.button("Analyze")


# ---- Model Loading ----

nlp, tagger, spell, spell_en = load_model()

#-------------------------------------------------------------
#Basic Features
#-------------------------------------------------------------

tab1, tab2, tab3 = st.tabs(["CEFR", "Overview", "Errors"])


with tab2:
    st.header("Content Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    try:
        basic = basic_features(text, nlp)
        word_count = basic['word_count']
        sentence_count = basic['sentence_count']
        avg_words = basic['average_word_per_sentence']
        doc = tokenize(text, nlp)
    
        with col1:
            st.metric(
                "Word Count",
                word_count,
                help="Total number of words in the essay"
            )
    
        with col2:
            st.metric(
                "Sentence Count",
                sentence_count,
                help="Total number of sentences"
            )
    
        with col3:
            st.metric(
                "Avg Words/Sentence",
                round(avg_words, 2),
                help="Average word count per sentence"
            )
    except Exception as e:
        st.error(f"Error in basic features: {str(e)}")
        st.stop()

    st.subheader('Lexical Diversity Score')

    words_list, lexical_density = lexical_diversity_score(doc)

    st.metric(
                "Lexical Diversity",
                round(lexical_density,2),
                help="Tells you the richness of unique vocabulary in your text"
            )


    st.subheader('MTLD')
    st.caption('Measure of Textual Lexical Diversity')

    lemmas = lemma_conversion(doc)
    mtld = mtld(lemmas)

    st.metric(
        'Your MTLD score',
        mtld,
        help = 'It is a lexical diversity metric used to measure how varied the vocabulary is in a text while being less sensitive to text length than traditional measures.'
    )


    st.subheader('Repitition Density')

    col1, col2, col3 = st.columns(3)

    st.write(f"\nTop repeated content words:")
    repitition_density = repetition_with_stop(doc)
    lexical_repitition = repetition_without_stop(doc)

    total_words = len([token for token in doc if not token.is_punct and not token.is_space and token.is_alpha])

    try:
        with col1:
            st.metric(
                'Total words',
                total_words
            )

        with col2:   
            st.metric(
                'Repitition Density',
                repitition_density,
                help= 'Measures how frequently words are repeated within a text relative to the total word count'
            )
        
        with col3:
            st.metric(
                'Lexical Repitition',
                lexical_repitition,
                help= 'Measures the proportion of content words (nouns, verbs, adjectives, adverbs) compared to the total number of words in a text.'
            )
    
    except Exception as e:
        st.error(f"Error in Repitition Density: {str(e)}")


    st.subheader('Clause Density')

    total_clause_found = clause_density(doc)
    st.metric(
        'Total Clauses Found',
        total_clause_found,
    )



with tab3:
    with st.expander("⚠️ About Error Detection"):
        st.markdown("""
    The grammar and error analysis in this section is generated automatically using linguistic feature extraction and rule-based heuristics. While the system is designed to detect common structural and grammatical patterns in German learner texts, there are high chances that it may produce false positives or overlook certain errors due to the used model's limitations (spaCy).

    The suggested target users of this feature are users who are between A1 to B1 level of German. The model's accuracy starts depleating with bigger clauses. Also, if you are a beginner of the language a bad sentence structure could also produce multiple false positives due to the way how spaCy's dependency parser works.

    Results are intended to provide guidance and learning insight rather than definitive linguistic judgment. For best accuracy, use texts with sufficient length (60+ words) and clear sentence structure.
    """)

    st.subheader('Subordinate Accuracy')
    sub_error_count, clause_count = subordinate_accuracy(doc)
    correct = clause_count - sub_error_count
    accuracy = round(correct / clause_count * 100, 2) if clause_count else 0

    st.write(f"Total Clauses: {clause_count}")
    st.write(f"Correct: {correct}")
    st.write(f"Wrong: {sub_error_count}")
    st.write(f"Accuracy: {accuracy}%")


    # Article Accuracy
    st.subheader('Article Accuracy')

    article_errors = article_error(doc, verbose=True)

    if article_errors == 0:
        st.success(f"🎉 Perfect! No article errors found. Total Errors: {article_errors}")
    else:
        st.error(f"Total Errors: {article_errors}")

    st.caption("⚠️ Do not completely rely on the results — they might be incorrect due to spaCy model limitations.")

    st.subheader('Verb Morphology')

    verb_errors = verb_morphology(doc, verbose=True)

    if verb_errors == 0:
        st.info('No Verb Morphology errors found')

    st.caption("⚠️ Do not completely rely on the results — they might be incorrect due to spaCy model limitations.")


    st.subheader("Preposition Case Checker")

    prep_errors = preposition_errors(doc, verbose=True)

    if prep_errors == 0:
        st.success(f"🎉 No preposition errors detected! (Total: {prep_errors})")
    else:
        st.error(f"🚨 {prep_errors} potential preposition case error(s) found")

    st.caption(
        "ℹ️ Only fixed prepositions (always Dative or always Accusative) are checked. "
        "Two-way prepositions (an, auf, in, etc.) are not included yet. "
        "spaCy morphology can sometimes be missing or inaccurate."
    )


    st.subheader('Capitalization Errors')

    cap_errors = cap_error(doc, verbose=True)

    st.write(f'Total Errors: {cap_errors}')


    st.subheader('Spelling Check')

    misspelled, spelling_error_count = spell_check(doc, spell, spell_en)

    st.write(f'Total Misspelled Words: {spelling_error_count}')
    st.write(misspelled)

    st.subheader("Case Errors (Pronoun Case Heuristic)")

    case_errors = case_error(text, tagger, nlp, verbose=True)
    st.write(f"Total Case Errors: {case_errors}")



    st.subheader('Total Error Count')

    v2_errors = v2_order(doc, text)

    sub_error_count, article_error_count, verb_error_count, case_error_count, cap_error_count, prep_error_count, v2_error_count = errors_count(
        sub_error_count, article_errors, verb_errors, case_errors, cap_errors, prep_errors, v2_errors
    )

    st.write(f'''
        Subordinate Errors: {sub_error_count}\n, 
        Article Errors: {article_error_count}\n,
        Verb Morphology Errors: {verb_error_count}\n,
        Case Errors: {case_error_count}\n,
            Capitalization Errors; {cap_error_count}\n,
            Preposition Errors: {prep_error_count},
            Verb Position Errors: {v2_error_count}
    ''')

    err_rate = error_rate(
        word_count,
        article_error_count,
        verb_error_count,
        sub_error_count,
        prep_error_count,
        case_error_count,
        cap_error_count,
        v2_error_count
    )

    st.error(f'Total Error Rate: {round(err_rate, 2)}')


with tab1: 
    st.header("Language Proficiency Level")
    st.write('Calculated LCI of text based on the uniqueness and complexity of your text')

    try:
        mtld_norm, adj_clause_norm, sent_norm, nomin_norm, dep_norm, discourse_norm = normalization(
            doc, mtld, avg_words, total_clause_found, sub_error_count, word_count, text
        )
    
        lci = lci(
            word_count, mtld_norm, adj_clause_norm, sent_norm, nomin_norm, dep_norm, 
            discourse_norm, sub_error_count, verb_error_count, case_error_count, 
            prep_error_count, article_error_count, cap_error_count, spelling_error_count
        )
    
        cefr_level = cefr(lci)
    
        # CEFR Level Display
        cefr_colors = {
            # Using your theme palette for consistency
            'A1': '#19C2C9',
            'A2': '#0FB8BF',
            'B1': '#05B2B9',
            'B2': '#00ADB5',
            'C1': '#007F85',
            'C2': '#004F53'
        }
    
        color = cefr_colors.get(cefr_level, '#00ADB5')
    
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {color} 0%, {color}cc 100%);
            color: #F3F4F4;
            padding: 3rem;
            border-radius: 14px;
            text-align: center;
            margin: 2rem 0;
        ">
            <p style="font-size: 1.2rem; opacity: 0.9; margin-bottom: 1rem;">Language Complexity Index (LCI)</p>
            <p style="font-size: 1.5rem; font-weight: 600; margin-bottom: 1.5rem;">{round(lci, 2)}</p>
            <p style="font-size: 0.9rem; opacity: 0.85; margin-bottom: 1.5rem;">Estimated Proficiency Level</p>
            <p style="font-size: 4rem; font-weight: 900; margin-bottom: 1rem; text-shadow: 0 4px 8px rgba(0,0,0,0.2);">{cefr_level}</p>
            <p style="font-size: 1rem; opacity: 0.95;">
                {'Beginner' if cefr_level in ['A1', 'A2'] else 'Intermediate' if cefr_level in ['B1', 'B2'] else 'Advanced'}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error in CEFR assessment: {str(e)}")


st.caption(
    "Automated grammar analysis based on linguistic feature extraction. "
    "Results may contain minor inaccuracies and are intended for learning guidance."
)
