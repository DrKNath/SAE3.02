# SAE3.02 grp : LABUBU
Développer des applications communicantes

## Master : 
Le master sert juste de "base de donné"

## Router :
Déchiffre et envoie au prochain saut

## Client :
Chiffre et envoi au premier au router 

## RUN
Premièrement vous devez créer la base de donnée, tout est dans la [docs bdd.md](docs/bdd.md)

Pour lancé les différent code, vous trouverez un requirement.txt qu'on vous invite à installé dans un environement virtuelle. 
Les étapes à suivre : 
se placé dans le dossier du projet
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
se placé dans le dossier du src

pour lancé les codes faites : 
### master
pour lancé le master vous devez avoir la base de donnée qui sois déjà mise en place et après remplacé les "" par les différente info (ne mettez pas les "" autour des différentes infos)
ex : ```python -m master.main 192.168.1.120 toto toto```

```
python -m master.main "@ip bdd" "user bdd" "mdp bdd"
```
### client
```
python -m client.main
```
### router
argument key_size permet de définir manuellement la taille de la clé en bits qu'auras le router (par défaut 8), plus la clé est grande plus l'envoi/ réception des messages seras longue et il va de même pour le chiffrement / déchiffrement. "key_size" est un variable numérique donc par exemple pour lancer un router avec une clé de 32 bits,ce sera, ```python -m router.main 32```

```
python -m router.main "key_size"
```
