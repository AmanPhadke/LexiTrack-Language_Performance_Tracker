# LexiTrack: German Language Performance Tracker

A comprehensive Streamlit-based application specifically created for my personal application for analyzing German language proficiency and text complexity. LexiTrack provides detailed linguistic analysis, error detection, and CEFR level assessment for German learner texts.

## 🎯 Features

### Content Analysis
- **Word Count** - Total number of words in the text
- **Sentence Count** - Number of sentences analyzed
- **Average Words per Sentence** - Readability metric
- **Lexical Diversity Score** - Measures vocabulary richness and uniqueness
- **MTLD (Measure of Textual Lexical Diversity)** - Advanced lexical diversity metric less sensitive to text length
- **Repetition Density** - Analyzes word repetition patterns with and without stop words
- **Clause Density** - Counts subordinate and relative clauses


### Error Detection & Analysis
The app identifies and flags common errors in German learner texts:

- **Subordinate Clause Accuracy** - Checks correct use of subordinate conjunctions (weil, dass, obwohl, wenn, etc.)
- **Article Accuracy** - Detects incorrect article usage (der, die, das, ein, eine, etc.)
- **Verb Morphology** - Identifies verb conjugation and tense errors
- **Preposition Case Checker** - Validates dative and accusative prepositions
- **Capitalization Errors** - Flags incorrect capitalization (especially for nouns)
- **Spelling Check** - Detects misspelled words in German and English
- **Case Errors (Pronoun Case Heuristic)** - Identifies incorrect pronoun cases
- **V2 Word Order** - Checks verb position in main clauses

### Language Proficiency Assessment
- **Language Complexity Index (LCI)** - Custom metric combining multiple linguistic features
- **CEFR Level Estimation** - Automatically assigns proficiency level (A1-C2)
- **Error Rate Calculation** - Overall error frequency per word count
- **Proficiency Classification** - Beginner, Intermediate, or Advanced

### Visualization
- Interactive Plotly charts and metrics
- Color-coded CEFR level display
- Detailed error breakdowns
- Top repeated words analysis

---

## 📋 Requirements

### System Requirements
- Python 3.10+
- 2GB RAM minimum (for spaCy and HanTa models)
- ~500MB disk space for language models

### Python Dependencies
All dependencies are listed in `requirements.txt`:
- **streamlit** - Web app framework
- **spacy** - NLP library for German text processing
- **pandas** - Data manipulation and analysis
- **plotly** - Interactive visualizations
- **pyspellchecker** - Spelling error detection
- **HanTa** - German lemmatizer and morphological tagger

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/AmanPhadke/LexiTrack-German_Language_Performance_Tracker.git
cd LexiTrack-German_Language_Performance_Tracker
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the spaCy German Model
```bash
python -m spacy download de_core_news_md
```

### 5. Ensure HanTa Model File
The file `morphmodel_ger.pgz` must be in the project root directory. If it's missing, HanTa will attempt to download it automatically on first run.

---

## 💻 Running the Application

Start the Streamlit app:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

---

## 📖 How to Use

### Step 1: Enter Your Text
- Paste or type your German essay/text in the text area
- Minimum recommended length: 60+ words for accurate analysis
- Click the "Analyze" button to begin
<img width="1782" height="608" alt="Screenshot 2026-03-21 162525" src="https://github.com/user-attachments/assets/04a30a84-5578-44d0-8f10-fe6ad28c2ea1" />

### Step 2: View Analysis Results
The app displays results in three tabs:

#### **CEFR Tab** - Language Proficiency Level
- Shows your Language Complexity Index (LCI)
- Displays estimated **CEFR Level** (A1-C2)
- Color-coded proficiency indicator
<img width="1808" height="853" alt="Screenshot 2026-03-21 162547" src="https://github.com/user-attachments/assets/841cdfc1-8b75-4d0a-9efc-651959f1f0c6" />


#### **Overview Tab** - Content Analysis
- Basic text statistics (word count, sentences, etc.)
- Lexical diversity metrics
- MTLD score
- Repetition density analysis
- Clause density breakdown
<img width="1518" height="702" alt="Screenshot 2026-03-21 162601" src="https://github.com/user-attachments/assets/63dbb282-c32a-4c3c-a977-29b635d10e4f" />
<img width="1779" height="785" alt="Screenshot 2026-03-21 162617" src="https://github.com/user-attachments/assets/3968fad9-3db5-4f95-b4e7-d01425fd40f8" />


#### **Errors Tab** - Grammar & Spelling Analysis
- Subordinate clause accuracy
- Article usage errors
- Verb morphology issues
- Preposition case errors
- Capitalization mistakes
- Spelling errors
- Pronoun case errors
- V2 word order violations
- **Total Error Count** with error rate
<img width="1775" height="674" alt="Screenshot 2026-03-21 162655" src="https://github.com/user-attachments/assets/2a242a17-c1f5-4b84-a909-edceab69c3a2" />
<img width="1763" height="838" alt="Screenshot 2026-03-21 162706" src="https://github.com/user-attachments/assets/c8c33c72-db15-4cbf-ba32-5f1a13ae25d7" />
<img width="1756" height="803" alt="Screenshot 2026-03-21 163002" src="https://github.com/user-attachments/assets/6bbe53f8-560a-4ed8-b1d6-80bd69bda9a6" />

---

## 🔍 Analysis Metrics Explained

### Lexical Diversity Score
**Range:** 0 to 1  
**What it measures:** Percentage of unique words relative to total words  
**Higher is better:** Indicates richer vocabulary usage

### MTLD (Measure of Textual Lexical Diversity)
**What it measures:** Average vocabulary richness across the text  
**Why it's useful:** Less affected by text length than traditional measures  
**Typical range:** 30-90 (higher = more diverse vocabulary)

### Repetition Density
**Measured with & without stop words**  
- **With stop words:** Includes common words (the, and, is)
- **Without stop words:** Focuses on content words (nouns, verbs, adjectives)  
**Higher values:** May indicate repetitive writing

### Clause Density
**What it measures:** Number of subordinate and relative clauses  
**Why it matters:** Complex clause use is a marker of advanced proficiency

### Error Rate
**Calculation:** `Total Errors / Word Count × 100`  
**Interpretation:**
- 0-2% = Excellent
- 2-5% = Good
- 5-10% = Fair
- 10%+ = Needs improvement

### CEFR Levels
- **A1** - Beginner
- **A2** - Elementary
- **B1** - Intermediate
- **B2** - Upper Intermediate
- **C1** - Advanced
- **C2** - Mastery

---

## ⚠️ Important Notes & Limitations

### Accuracy Considerations
- The analysis uses **spaCy's dependency parser**, which has limitations with complex sentence structures
- **Beginner texts (A1-A2)** may produce false positives in error detection due to non-standard sentence structure
- Results are most accurate for texts with:
  - Clear sentence boundaries
  - Standard German grammar
  - 60+ words minimum is recommended

### Error Detection
- Grammar detection is rule-based and heuristic-driven
- Not all errors may be caught (especially nuanced ones)
- Some false positives may occur, especially with:
  - Ambiguous sentence structures
  - Poetry or creative writing
  - Colloquial German

### Best Practices
1. Write clear, well-structured sentences
2. Use standard German grammar and spelling
3. For best results, submit 60+ word texts
4. Review suggested errors but use your judgment
5. Use results as learning guidance, not absolute truth

---

## 🛠️ Technical Architecture

### Core Components

**1. Language Processing**
- spaCy (v3.5.0) - Tokenization, POS tagging, dependency parsing
- HanTa - German lemmatization and morphological analysis

**2. Analysis Modules**
- Basic Features - Word/sentence counts and content ratios
- Lexical Analysis - Diversity scores and MTLD calculation
- Error Detection - Grammar and spelling error identification
- Proficiency Assessment - CEFR level calculation

**3. Visualization**
- Streamlit - Web UI and interactive components
- Plotly - Interactive charts and metrics

---

## 🐛 Troubleshooting

### Issue: "Can't find model 'de_core_news_md'"
**Solution:**
```bash
python -m spacy download de_core_news_md
```

### Issue: "HanTa model file not found"
**Solution:** Ensure `morphmodel_ger.pgz` is in the project root, or it will auto-download on first run

### Issue: App runs very slowly
**Possible causes:**
- First time loading models (normal)
- Large text input (>10,000 words)
- Insufficient RAM
**Solution:** Restart the app or reduce text size

### Issue: Error detection seems inaccurate
**Why:** spaCy has limitations with complex or non-standard structures  
**Solution:** Check error flags but verify with German grammar resources (read the notice block in the error tab at the top)

---

## 📊 Example Output

```
Input: "Ich bin ein Student und ich lerne Deutsch."

Results:
- Word Count: 8
- Sentence Count: 1
- Lexical Diversity: 0.75
- MTLD: 6.5
- Repetition Density: 12.5%
- Subordinate Clauses: 0
- Errors Found: 1 (capitalization: "Student" after lowercase)
- Estimated CEFR Level: A1
- Error Rate: 12.5%
```

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Enhanced error detection accuracy
- Support for more languages
- Better handling of colloquial German
- Additional proficiency assessment metrics

---

## 📝 License

This project is open source. Please check the LICENSE file for details.

---

## 👨‍💻 Author

**Aman Phadke**  
GitHub: [@AmanPhadke](https://github.com/AmanPhadke)

---

## 🙏 Acknowledgments

- **spaCy** - Industrial-strength NLP
- **HanTa** - German morphological analysis
- **Streamlit** - Making ML apps easy to build
- **Plotly** - For Vocabulary Growth visualization
- **Pandas** - For creating dataframes and basic functionalities

---

## 📞 Support & Feedback

For issues, suggestions, or feedback:
1. Open an GitHub issue
2. Provide details about the problem or suggestion
3. Include example text if reporting errors

---

## 🔄 Updates & Roadmap

Potential future features:
- [ ] Multi-language support
- [ ] Advanced ML-based error detection
- [ ] Text difficulty scoring
- [ ] Writing style analysis
- [ ] Personalized learning recommendations
- [ ] Export analysis reports

---

**Last Updated:** March 2026  
**Version:** 1.0.0
