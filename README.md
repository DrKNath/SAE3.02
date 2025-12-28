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
‘‘‘
    ce placé dans le dossier du projet
    faire python -m venv venv

    ### sous MacOS / Linux
    source venv/bin/activate
    ### Windows
    venv\Scripts\activate

    après installé les module qui faut avec le requirements.txt
    pip install -r requirements.txt

    pour lancé les codes faites : 
    ### master
    python -m master.main
    ### client
    python -m client.main
    ### router
    python -m router.main

‘‘‘