# BDD
Cette partie à été réaliser sur une machine sous Linux.

## Setup
Dans votre logiciel de basse de donné vous allez devoir crée un basse de donné nommé ```oignon_db```.
Dans cette base de donné vous allez devoir crée plusieur tables: 
- tables 1 : active_nodes avec comme colone, name (VARCHAR(255) PRIMARY KEY), type (VARCHAR(50)), ip (VARCHAR(50)), port(INT), public_key (TEXT)
- tables 2 : logs avec comme colonne,id (INT AUTO_INCREMENT PRIMARY KEY), sender (VARCHAR(255)), receiver (VARCHAR(255)), content (TEXT), timestamp (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)


### Script SQL
```
CREATE DATABASE oignon_db;
USE oignon_db;

CREATE TABLE logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender VARCHAR(255),
    receiver VARCHAR(255),
    content TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE active_nodes (
    name VARCHAR(255) PRIMARY KEY,
    type VARCHAR(50),
    ip VARCHAR(50),
    port INT,
    public_key TEXT
);

CREATE USER 'toto'@'%' IDENTIFIED BY 'toto';
GRANT ALL PRIVILEGES ON oignon_db.* TO 'toto'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

# ⚠️ Attention
Dans la partie où l'on crée l'utilisateur nous vous invitons à changé le nom de ce dernier et le mot de passe.

