# SAE3.02
Développer des applications communicantes

## Master : 
Le master sert juste de "base de donné"

## Router :
Décrypt et envoie au prochain saut

## Client :
Chiffre et envoi au premier au router 

## RUN
Pour lancé les différent code, vous trouverez un requirement.txt qu'on vous invite à installé dans un environement virtuelle. 
Les étapes à suivre : 
ce placé dans le dossier du projet
faire 
```
python -m venv venv
```

### sous MacOS / Linux
```
source venv/bin/activate
```
### Windows
```
venv\Scripts\activate
```

après installé les module qui faut avec le requirements.txt
```
pip install -r requirements.txt
```
ce placé dans le dossier du src

pour lancé les codes faites : 
### master
pour lancé le master vous devez avoir la base de donné qui sous déjà mit en place et après remplacé les "" par les différente info (ne mettait pas les "" autour des diffénte info)
ex : ```python -m master.main 192.168.1.120 toto toto```

```
python -m master.main "@ip bdd" "user bdd" "mdp bdd"
```
### client
```
python -m client.main
```
### router
argument key_size permet de définir manuellement la taille de la clé en bits qu'au le router (par défaut 8), plus la clé est grande plus l'envoi/ reception des message sera longue et il va de même pour le chiffrement / déchiffrement. "key_size" est un variable numérique donc exemple pour lancé un router avec une clé de 32 bits sa sera, ```python -m router.main 32```

```
python -m router.main "key_size"
```
