def get_stopwords(words):
    """Detect language used in chat then return corresponding stopwords."""
    d = {lang: len(stopwords.intersection(words)) for lang, stopwords in STOPWORDS.items()}
    lang_used = max(d, key=d.get)
    return STOPWORDS[lang_used]

STOPWORDS = {
    'en': {
		# get from default wordcloud stopwords with additional stopwords
        'above','up','at','own','i','my','of','those',"where's",'yourselves','each','has','while','in',
        'your','r','having',"they'd","we'd",'same','also','did','them',"wasn't","don't",'here','herself',
        'all','itself','an','cannot','doing',"she'll",'some',"she'd",'then','during','his','over',
        'yourself',"we'll",'nor','have','its',"shouldn't",'off','being',"you've",'ours','for','only',
        'their','than',"you'll",'hers','he',"you're",'further','which',"here's","who's",'both',"why's",
        'could','down',"mustn't",'again',"let's",'from',"weren't",'would','theirs',"doesn't",'ourselves',
        "she's",'through','himself','ought','against','how',"we've","i'll",'very','get',"he'd",'who',"i'd",
        'should','can','what','do','under',"aren't",'been','our','few',"he's",'http',"won't",'after',
        "they're",'where',"hadn't",'but',"i've",'www','she','therefore','had','is',"hasn't","it's",'we',
        'him','about','otherwise','themselves',"wouldn't","i'm","can't",'yours','since','such',"couldn't",
        "what's",'you','and','because',"didn't",'if','before','a',"shan't","you'd",'into','any','by','so',
        'between','once',"they'll",'com','the','more','me','why','or',"he'll",'until','other','was','no',
        "they've",'does',"that's","there's","when's",'ever','be',"haven't",'however','out','am','k','these',
        'are','else','her','it','that','with','there','hence','like','they','on','below','myself','not','to',
        "we're","isn't",'most','too','were','when','just',"how's",'as','this','whom','shall','u','ok','o','oh',
        'ha','haha','hahaha', 'hahahaha''hoho','hi'}

}