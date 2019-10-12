#      Trust and Believe – Should We?
# Evaluating the Trustworthiness of Twitter Users

This model is used to calculate the reputation score for a twitter user. The model is base on both the user level and content level entity for each twitter user. The details are given in the paper.

## Description
These scripts are used to extract different features for twitter user and are then used to calculate the reputation score for each twitter users. We generate a dataset for 500 twitter users and then used different regression models to find the one that best fit to our model.

## Organization
The project consist of the following files:
### data_set.csv
The datasetr consist of the 20 features of 500 twitter users including the reputation score for eah user. These features consist of both the user level and content level entities.
### feature_extraction.py
This python scipt is used to calculate the reputation score of a twitter user based on cite

- Social reputation of the user
- Content score of the tweets
- Tweets credibility
- Index score for the number of re-tweets and likes

### twitter_reputation.ipynb
We used different regression models to test its performance on our generated dataset. We train and evaluate our models using different regression models.
Training and testing three regression models:
1. Multilayr perceptron
2. Deep neural network
3. Linear regression
### twitter_credentials.py
In order to extract the features of twitter users first you need to authenticate yourself by providing the credentils given in this file.
### twitter_user_names.txt
This text file consist of all the 500 twitter user names. All of them are politicians and most of them are from pakistan. We remove the names of all those politicians whose accounts are private. In addition, all those politicians who has no followers/followings are not in the list. 

## References
[1] https://stackoverflow.com/questions/38881314/twitter-data-to-csv-getting-error-when-trying-to-add-to-csv-file

[2] https://stackoverflow.com/questions/48157259/python-tweepy-api-user-timeline-for-list-of-multiple-users-error

[3] https://gallery.azure.ai/Notebook/Computing-Influence-Score-for-Twitter-Users-1

[4] https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPClassifier.html

[5] https://towardsdatascience.com/deep-neural-networks-for-regression-problems-81321897ca33
