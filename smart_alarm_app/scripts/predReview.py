import pandas as pd
import seaborn as sb
from sklearn import preprocessing, svm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from smart_alarm_app.models import Night

def main():
    #Provedu načtení csv a vyberu pouze hodnoty, které neobsahují nulové hodnoty
    df = pd.read_csv('static/csv/allnights.csv')
    df_binary = df.dropna()

    #Regrese vyžaduje pouze číselné hodnoty 

    #Převedu všechy False na 0 a True na 1
    df_values = df_binary.replace({True: 1, False: 0})
    #Převedu délku spánku na sekundy
    df_values['duration'] = pd.to_timedelta(df_values['duration']).apply(lambda x: x.total_seconds())
    #Odstraň první sloupec id
    df_final = df_values.drop('id', axis=1)

    #Rozdělím dataset na závislé a nezávislé proměnné 
    nezavisle = df_final.iloc[:, :-1]
    zavisla = df_final["review_sleep"]
    x = nezavisle.values
    y = zavisla.values

    #Během testování - Rozdělím na testovací a trénovací data
    #x_train, x_test, y_train, y_test = train_test_split(x,y,test_size=0.25,random_state=0)
    #regrese = LinearRegression()
    #regrese.fit(x_train,y_train)

    #y_train_pred = regrese.predict(x_train)
    #y_test_pred = regrese.predict(x_test)

    #Webová verze bez rozdělení na test/train
    regrese = LinearRegression()
    regrese.fit(x,y)

    #Samotná predikce
    new_df = pd.read_csv('static/csv/onenight.csv')
    #Úprava hodnot
    new_df_values = new_df.replace({True: 1, False: 0})
    new_df_values['duration'] = pd.to_timedelta(new_df['duration']).apply(lambda x: x.total_seconds())
    new_df_final = new_df_values.drop('id', axis=1)
    #vybrání nezávislých proměnných
    new_nezavisle = new_df_final.iloc[:, :-1]
    #Predikce hodnoty
    pred_review = regrese.predict(new_nezavisle.values)
    Night.objects.filter(active=True).update(pred_review=pred_review)
