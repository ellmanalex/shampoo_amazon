import pandas as pd
import numpy as np
import re

pd.set_option('display.max_rows', 5000)
pd.set_option('display.min_rows', 4000)

shampoo = pd.read_csv('shampoo_scrape_1.csv')
best_selling = pd.read_csv('bestselling_shampoos_.csv')
shampoo_2 = pd.read_csv('shamoo_scrape_2.csv')
shampoo['best_selling'] = None
best_selling['best_selling'] = 'yes'

# review count
best_selling[['review_count']] = best_selling[['review_count']].applymap(lambda x: int(''.join(re.findall('[1-9]', str(x)))))

#concat dataframes
shampoo = pd.concat([best_selling,shampoo,shampoo_2])#.drop_duplicates().reset_index(drop= True)
shampoo.drop_duplicates(subset = "asin", keep = False, inplace= True)


# convert review counts containing text to 0 as these products have 0 reviews
review_replace = {'Amazon Best Sellers Rank:':[0]}
shampoo = shampoo.replace({'review_count':review_replace})

# convert review count to integer
shampoo[['review_count']] = shampoo[['review_count']].applymap(lambda x: int(re.findall('\d+', str(x))[0]))
shampoo['review_count']=shampoo['review_count'].astype('int')


# find values that are not standard format in ratings
#rating_mask = shampoo[['rating']].applymap(lambda x: re.match(r'[1-9]',x) ==None)

#shampoo[['rating']][rating_mask['rating']]

# change those values to none type
shampoo.loc[shampoo['rating']=='Be the first to write a review','rating'] = None

# convert string format of rating to integer
shampoo[['rating']] = shampoo[['rating']].applymap(lambda x: x[0:3] if x is not None else x)
shampoo[['rating']]= shampoo[['rating']].applymap(lambda x: ''.join(re.findall('[1-9.]', str(x)))if x is not None else x)

#shampoo['rating']=shampoo['rating'].astype('float')

# price per column to seperate columns for value and unit
price_per_aslist = shampoo[['price_per']].applymap(lambda x: x.split('/'))
shampoo = shampoo.assign(price_per_value = [x[0] for x in price_per_aslist['price_per']])
shampoo = shampoo.assign(price_per_unit = [x[1] for x in price_per_aslist['price_per']])

# convert price_per_value column to int
shampoo[['price_per_value']] = shampoo[['price_per_value']].applymap(lambda x: ''.join(re.findall('[1-9.]',x)))

# need to change irrelevant values to none type and then change column to float
shampoo.loc[shampoo['price_per_value'] == '.'] = None
shampoo['price_per_value'] = shampoo['price_per_value'].astype('float')

# make new channel column that categorizes to "FBA", "marketplace", "owned", "DSV"
def merch_assign(x):
    try:
        if 'Ships from and sold by Amazon.com' in x:
            return 'Owned'
        if 'Fulfilled by Amazon' in x:
            return 'FBA'
        if 'Amazon' not in x:
            return 'Marketplace'
    except:
        return x

shampoo['channel'] = shampoo[['merchant']].applymap(lambda x: merch_assign(x))

#input no value for non-best selling shampoo
shampoo[['best_selling']] = shampoo[['best_selling']].fillna(value='no')


# natural language processing of description
# create new column with description in lower case
shampoo['nlp_description'] = shampoo['description'].str.lower()

# create new dataframe with null description rows removed
description_mask = shampoo['nlp_description'].isnull() == False
description_df = shampoo.loc[description_mask,:]

# nlp pre-processing:
#remove , and . and replace with a space
description_df['nlp_description'] = description_df['nlp_description'].apply(lambda x: re.sub('[,.]', ' ', x))

#remove all extra spaces
description_df['nlp_description'] = description_df['nlp_description'].apply(lambda x: re.sub('\s+', ' ', x))

# remove all remaining punctuation
description_df['nlp_description'] = description_df['nlp_description'].apply(lambda x: re.sub('[^\w\s]', '', x))

# group view
best_seller_group = shampoo.groupby('best_selling',)
best_seller_group.agg(['mean','std','median'])


rating_mask = shampoo['rating'].isnull()==False
rating_group = shampoo.loc[rating_mask,:]
rating_group['rating']=rating_group['rating'].astype('float')
rating_grouped = rating_group.groupby('best_selling',)

rating_grouped.agg(['mean','std','median'])

# Natural Language Processing
from nltk.corpus import stopwords
stop = stopwords.words('english')
from textblob import TextBlob
from nltk import PorterStemmer
stemmer = PorterStemmer()
import nltk

df = pd.read_csv('description_df')
df['nlp_description'] = df['nlp_description'].astype('string')

# add product specific stop words
stop.extend(['shampoo','conditioner','soap','cleanse','hair','head','shoulders','loréal', 'pari','product','help','use','free','make','type'])

#Pre Processing
#remove stop words
df['nlp_description'] = df['nlp_description'].apply(lambda text: " ".join(word for word in text.split() if word not in stop))
df['nlp_description'] = df['nlp_description'].astype('string')
#tokenize
df['nlp_description'] = df['nlp_description'].apply(lambda text: TextBlob(text).words)
# stemming and remove stop words again
df[['nlp_description']] = df[['nlp_description']].applymap(lambda text: [stemmer.stem(word) for word in text])
df['nlp_description'] = df['nlp_description'].apply(lambda text: [word for word in text if word not in stop])
# create bestselling dataframe
df_bestselling = df.loc[df['best_selling']=='yes',:]

# extract corpus of best_sellling descriptions and retokenize
f = df_bestselling['nlp_description'].apply(lambda x: ' '.join(x))
f = [x for x in f]
f = ''.join(f)
f = TextBlob(f).words
f = nltk.FreqDist(f)

# repeat on total df
g = df['nlp_description'].apply(lambda x: ' '.join(x))
g = [x for x in g]
g = ''.join(g)
g = TextBlob(g).words
g = nltk.FreqDist(g)



