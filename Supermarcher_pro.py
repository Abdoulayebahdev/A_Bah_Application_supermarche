# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 17:25:38 2026

@author: lenovo
"""

'''
SUPERMARCHÉ PRO
Application de gestion en Python
Code source complet — un seul fichier Python
Code source complet
'''


import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import os
 
# ============================================================
# SUPERMARCHE PRO
# Application complete de gestion de supermarche
# Python + Tkinter + SQLite
# Un seul fichier Python
# ============================================================
 
# ---------------- COULEURS ----------------
BLEU_FONCE = "#172554"
BLEU = "#2563EB"
BLEU_CLAIR = "#DBEAFE"
VERT = "#16A34A"
VERT_CLAIR = "#DCFCE7"
ROUGE = "#DC2626"
ROUGE_CLAIR = "#FEE2E2"
ORANGE = "#F59E0B"
ORANGE_CLAIR = "#FEF3C7"
VIOLET = "#7C3AED"
VIOLET_CLAIR = "#EDE9FE"
FOND = "#F3F6FA"
BLANC = "#FFFFFF"
TEXTE = "#111827"
GRIS = "#6B7280"
BORDURE = "#D1D5DB"
 
SEUIL_STOCK = 5
FICHIER_DB = "supermarche.db"
 
role_connecte = ""
utilisateur_connecte = ""
panier = []
 
 
# ============================================================
# BASE DE DONNEES
# ============================================================
 
def connexion_db():
    return sqlite3.connect(FICHIER_DB)
 
 
def creer_base():         
    db = connexion_db()
    c = db.cursor()
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT UNIQUE NOT NULL,
            mot_de_passe TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS produits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            nom TEXT NOT NULL,
            categorie TEXT,
            prix REAL NOT NULL,
            quantite INTEGER NOT NULL,
            fournisseur TEXT
        )
    """)
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS fournisseurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            telephone TEXT,
            email TEXT
        )
    """)
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            telephone TEXT,
            email TEXT
        )
    """)
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS ventes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE NOT NULL,
            vendeur TEXT NOT NULL,
            client TEXT,
            total REAL NOT NULL,
            paiement REAL NOT NULL,
            monnaie REAL NOT NULL,
            date TEXT NOT NULL
        )
    """)
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS lignes_vente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vente_id INTEGER NOT NULL,
            code_produit TEXT NOT NULL,
            nom_produit TEXT NOT NULL,
            quantite INTEGER NOT NULL,
            prix_unitaire REAL NOT NULL,
            total REAL NOT NULL
        )
    """)
 
    c.execute("SELECT COUNT(*) FROM utilisateurs")
    if c.fetchone()[0] == 0:
        c.execute(
            "INSERT INTO utilisateurs (nom, mot_de_passe, role) VALUES (?, ?, ?)",
            ("admin", "1234", "Administrateur")
        )
        c.execute(
            "INSERT INTO utilisateurs (nom, mot_de_passe, role) VALUES (?, ?, ?)",
            ("caissier", "1234", "Caissier")
        )
 
    db.commit()
    db.close()
 
 
def executer(requete, parametres=()):
    db = connexion_db()
    c = db.cursor()
    c.execute(requete, parametres)
    resultat = c.fetchall()
    db.commit()
    db.close()
    return resultat
 
 
# ============================================================
# OUTILS
# ============================================================
 
def obtenir_produit(code):
    resultat = executer("""
        SELECT id, code, nom, categorie, prix, quantite, fournisseur
        FROM produits
        WHERE code=?
    """, (code,))
    if len(resultat) > 0:
        return resultat[0]
    return None
 
 
def nombre_produits():
    return executer("SELECT COUNT(*) FROM produits")[0][0]
 
 
def total_stock():
    return executer("SELECT COALESCE(SUM(quantite), 0) FROM produits")[0][0]
 
 
def nombre_ventes():
    return executer("SELECT COUNT(*) FROM ventes")[0][0]
 
 
def chiffre_affaires():
    return executer("SELECT COALESCE(SUM(total), 0) FROM ventes")[0][0]
 
 
def stock_faible():
    return executer(
        "SELECT COUNT(*) FROM produits WHERE quantite <= ?",
        (SEUIL_STOCK,)
    )[0][0]
 
 
def format_prix(valeur):
    return f"{valeur:,.0f} GNF".replace(",", " ")
 
 
def prochain_numero():
    date = datetime.now().strftime("%Y%m%d")
    resultat = executer(
        "SELECT COUNT(*) FROM ventes WHERE numero LIKE ?",
        (date + "%",)
    )
    numero = resultat[0][0] + 1
    return f"{date}-{numero:04d}"
 
 
def nettoyer():
    for widget in fenetre.winfo_children():
        widget.destroy()
 
 
# ============================================================
# DESIGN
# ============================================================
 
def bouton(parent, texte, commande, couleur=BLEU, largeur=20):
    b = tk.Button(
        parent,
        text=texte,
        command=commande,
        width=largeur,
        bg=couleur,
        fg=BLANC,
        activebackground=couleur,
        activeforeground=BLANC,
        font=("Arial", 10, "bold"),
        bd=0,
        relief="flat",
        cursor="hand2",
        padx=8,
        pady=9
    )
 
    b.bind("<Enter>", lambda e: b.config(relief="raised"))
    b.bind("<Leave>", lambda e: b.config(relief="flat"))
 
    return b
 
 
def champ(parent, largeur=30):
    return tk.Entry(
        parent,
        width=largeur,
        font=("Arial", 11),
        bg=BLANC,
        fg=TEXTE,
        relief="solid",
        bd=1
    )
 
 
def titre_page(parent, texte):
    tk.Label(
        parent,
        text=texte,
        bg=FOND,
        fg=TEXTE,
        font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=28, pady=(22, 12))
 
 
def carte_stat(parent, titre, valeur, couleur, ligne, colonne):
    cadre = tk.Frame(
        parent,
        bg=BLANC,
        highlightbackground=BORDURE,
        highlightthickness=1
    )
    cadre.grid(
        row=ligne,
        column=colonne,
        padx=8,
        pady=8,
        sticky="nsew"
    )
 
    tk.Frame(cadre, bg=couleur, height=5).pack(fill="x")
 
    tk.Label(
        cadre,
        text=titre,
        bg=BLANC,
        fg=GRIS,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", padx=16, pady=(14, 4))
 
    tk.Label(
        cadre,
        text=valeur,
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 19, "bold")
    ).pack(anchor="w", padx=16, pady=(0, 15))
 
 
def retour_dashboard():
    ouvrir_dashboard(role_connecte, utilisateur_connecte)
 
 
def deconnexion():
    global role_connecte, utilisateur_connecte, panier
 
    role_connecte = ""
    utilisateur_connecte = ""
    panier = []
 
    afficher_connexion()
 
 
# ============================================================
# CONNEXION
# ============================================================
 
def se_connecter(entree_nom, entree_mdp):
    global role_connecte, utilisateur_connecte
 
    nom = entree_nom.get().strip()
    mdp = entree_mdp.get().strip()
 
    resultat = executer(
        "SELECT role FROM utilisateurs WHERE nom=? AND mot_de_passe=?",
        (nom, mdp)
    )
 
    if len(resultat) > 0:
        utilisateur_connecte = nom
        role_connecte = resultat[0][0]
        ouvrir_dashboard(role_connecte, nom)
    else:
        messagebox.showerror(
            "Connexion",
            "Nom d'utilisateur ou mot de passe incorrect."
        )
 
 
def afficher_connexion():
    nettoyer()
 
    fenetre.unbind("<Return>")
 
    cadre = tk.Frame(fenetre, bg=BLEU_FONCE)
    cadre.pack(fill="both", expand=True)
 
    gauche = tk.Frame(cadre, bg=BLEU_FONCE, width=520)
    gauche.pack(side="left", fill="both", expand=True)
    gauche.pack_propagate(False)
 
    tk.Label(
        gauche,
        text="SUPERMARCHE",
        bg=BLEU_FONCE,
        fg=BLANC,
        font=("Arial", 32, "bold")
    ).pack(pady=(180, 10))
 
    tk.Label(
        gauche,
        text="Gestion • Stock • Caisse • Ventes",
        bg=BLEU_FONCE,
        fg="#BFDBFE",
        font=("Arial", 12)
    ).pack()
 
    droite = tk.Frame(cadre, bg=BLANC, width=500)
    droite.pack(side="right", fill="both", expand=True)
    droite.pack_propagate(False)
 
    box = tk.Frame(droite, bg=BLANC)
    box.place(relx=0.5, rely=0.5, anchor="center")
 
    tk.Label(
        box,
        text="Bienvenue",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 25, "bold")
    ).pack(anchor="w")
 
    tk.Label(
        box,
        text="Connectez-vous pour acceder a votre espace.",
        bg=BLANC,
        fg=GRIS,
        font=("Arial", 10)
    ).pack(anchor="w", pady=(4, 25))
 
    tk.Label(
        box,
        text="Nom d'utilisateur",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")
 
    entree_nom = champ(box, 32)
    entree_nom.pack(pady=(6, 15), ipady=7)
 
    tk.Label(
        box,
        text="Mot de passe",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 10, "bold")
    ).pack(anchor="w")
 
    entree_mdp = champ(box, 32)
    entree_mdp.config(show="*")
    entree_mdp.pack(pady=(6, 20), ipady=7)
 
    bouton(
        box,
        "SE CONNECTER",
        lambda: se_connecter(entree_nom, entree_mdp),
        BLEU,
        27
    ).pack(fill="x")
 
    tk.Label(
        box,
        text="Admin : admin / 1234    |    Caissier : caissier / 1234",
        bg=BLANC,
        fg=GRIS,
        font=("Arial", 8)
    ).pack(pady=18)
 
    entree_nom.focus()
 
    fenetre.bind(
        "<Return>",
        lambda e: se_connecter(entree_nom, entree_mdp)
    )
 
 
# ============================================================
# MENU
# ============================================================
 
def menu_lateral(parent):
    menu = tk.Frame(parent, bg=BLEU_FONCE, width=220)
    menu.pack(side="left", fill="y")
    menu.pack_propagate(False)
 
    tk.Label(
        menu,
        text="SUPERMARCHE",
        bg=BLEU_FONCE,
        fg=BLANC,
        font=("Arial", 18, "bold")
    ).pack(pady=(25, 4))
 
    tk.Label(
        menu,
        text=role_connecte.upper(),
        bg=BLEU_FONCE,
        fg="#93C5FD",
        font=("Arial", 9, "bold")
    ).pack(pady=(0, 25))
 
    bouton(
        menu, "TABLEAU DE BORD",
        retour_dashboard, BLEU_FONCE, 19
    ).pack(pady=3)
 
    bouton(
        menu, "PRODUITS",
        ouvrir_produits, BLEU_FONCE, 19
    ).pack(pady=3)
 
    bouton(
        menu, "STOCK",
        ouvrir_stock, BLEU_FONCE, 19
    ).pack(pady=3)
 
    if role_connecte == "Administrateur":
        bouton(
            menu, "FOURNISSEURS",
            ouvrir_fournisseurs, BLEU_FONCE, 19
        ).pack(pady=3)
 
        bouton(
            menu, "CLIENTS",
            ouvrir_clients, BLEU_FONCE, 19
        ).pack(pady=3)
 
        bouton(
            menu, "UTILISATEURS",
            ouvrir_utilisateurs, BLEU_FONCE, 19
        ).pack(pady=3)
 
    bouton(
        menu, "CAISSE",
        ouvrir_caisse, VERT, 19
    ).pack(pady=12)
 
    bouton(
        menu, "VENTES",
        ouvrir_ventes, BLEU_FONCE, 19
    ).pack(pady=3)
 
    bouton(
        menu, "STATISTIQUES",
        ouvrir_statistiques, BLEU_FONCE, 19
    ).pack(pady=3)
 
    bouton(
        menu, "ALERTES STOCK",
        ouvrir_alertes, ORANGE, 19
    ).pack(pady=12)
 
    bouton(
        menu, "DECONNEXION",
        deconnexion, ROUGE, 19
    ).pack(side="bottom", pady=22)
 
 
# ============================================================
# TABLEAU DE BORD
# ============================================================
 
def ouvrir_dashboard(role, utilisateur):
    nettoyer()
 
    conteneur = tk.Frame(fenetre, bg=FOND)
    conteneur.pack(fill="both", expand=True)
 
    menu_lateral(conteneur)
 
    principal = tk.Frame(conteneur, bg=FOND)
    principal.pack(side="right", fill="both", expand=True)
 
    header = tk.Frame(principal, bg=BLANC, height=75)
    header.pack(fill="x")
    header.pack_propagate(False)
 
    tk.Label(
        header,
        text="Tableau de bord",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 23, "bold")
    ).pack(side="left", padx=25)
 
    tk.Label(
        header,
        text="Connecte : " + utilisateur,
        bg=BLANC,
        fg=GRIS,
        font=("Arial", 10)
    ).pack(side="right", padx=25)
 
    tk.Label(
        principal,
        text="Vue generale de votre activite",
        bg=FOND,
        fg=GRIS,
        font=("Arial", 11)
    ).pack(anchor="w", padx=25, pady=(20, 5))
 
    cartes = tk.Frame(principal, bg=FOND)
    cartes.pack(fill="x", padx=17)
 
    for i in range(4):
        cartes.grid_columnconfigure(i, weight=1)
 
    carte_stat(
        cartes, "PRODUITS",
        str(nombre_produits()), BLEU, 0, 0
    )
 
    carte_stat(
        cartes, "STOCK TOTAL",
        str(total_stock()), VERT, 0, 1
    )
 
    carte_stat(
        cartes, "VENTES",
        str(nombre_ventes()), VIOLET, 0, 2
    )
 
    carte_stat(
        cartes, "CHIFFRE D'AFFAIRES",
        format_prix(chiffre_affaires()), ORANGE, 0, 3
    )
 
    zone = tk.Frame(principal, bg=FOND)
    zone.pack(fill="both", expand=True, padx=25, pady=18)
 
    gauche = tk.Frame(
        zone,
        bg=BLANC,
        highlightbackground=BORDURE,
        highlightthickness=1
    )
    gauche.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(0, 8)
    )
 
    tk.Label(
        gauche,
        text="Actions rapides",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 15, "bold")
    ).pack(anchor="w", padx=20, pady=(20, 15))
 
    bouton(
        gauche, "NOUVELLE VENTE",
        ouvrir_caisse, VERT, 25
    ).pack(pady=6)
 
    bouton(
        gauche, "CONSULTER LES PRODUITS",
        ouvrir_produits, BLEU, 25
    ).pack(pady=6)
 
    bouton(
        gauche, "VOIR LES VENTES",
        ouvrir_ventes, VIOLET, 25
    ).pack(pady=6)
 
    bouton(
        gauche, "VOIR LES ALERTES",
        ouvrir_alertes, ORANGE, 25
    ).pack(pady=6)
 
    droite = tk.Frame(
        zone,
        bg=BLANC,
        highlightbackground=BORDURE,
        highlightthickness=1
    )
    droite.pack(
        side="right",
        fill="both",
        expand=True,
        padx=(8, 0)
    )
 
    tk.Label(
        droite,
        text="Etat du stock",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 15, "bold")
    ).pack(anchor="w", padx=20, pady=(20, 10))
 
    faibles = stock_faible()
 
    if faibles > 0:
        tk.Label(
            droite,
            text=f"{faibles} produit(s) necessitent votre attention.",
            bg=ROUGE_CLAIR,
            fg=ROUGE,
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        ).pack(fill="x", padx=20, pady=10)
    else:
        tk.Label(
            droite,
            text="Stock correct. Aucune alerte.",
            bg=VERT_CLAIR,
            fg=VERT,
            font=("Arial", 11, "bold"),
            padx=15,
            pady=15
        ).pack(fill="x", padx=20, pady=10)
 
    tk.Label(
        droite,
        text="Dernieres ventes",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 12, "bold")
    ).pack(anchor="w", padx=20, pady=(15, 8))
 
    dernieres = executer("""
        SELECT numero, vendeur, total
        FROM ventes
        ORDER BY id DESC
        LIMIT 5
    """)
 
    for v in dernieres:
        tk.Label(
            droite,
            text=f"{v[0]}  •  {format_prix(v[2])}  •  {v[1]}",
            bg=BLANC,
            fg=GRIS,
            font=("Arial", 9)
        ).pack(anchor="w", padx=20, pady=3)
 
 
# ============================================================
# PRODUITS
# ============================================================
 
def actualiser_produits(tree, recherche=""):
    for ligne in tree.get_children():
        tree.delete(ligne)
 
    if recherche:
        produits = executer("""
            SELECT code, nom, categorie, prix, quantite, fournisseur
            FROM produits
            WHERE code LIKE ?
               OR nom LIKE ?
               OR categorie LIKE ?
            ORDER BY id DESC
        """, (
            "%" + recherche + "%",
            "%" + recherche + "%",
            "%" + recherche + "%"
        ))
    else:
        produits = executer("""
            SELECT code, nom, categorie, prix, quantite, fournisseur
            FROM produits
            ORDER BY id DESC
        """)
 
    for p in produits:
        tag = "faible" if p[4] <= SEUIL_STOCK else ""
 
        tree.insert(
            "",
            "end",
            values=(
                p[0],
                p[1],
                p[2] or "-",
                format_prix(p[3]),
                p[4],
                p[5] or "-"
            ),
            tags=(tag,)
        )
 
 
def ouvrir_produits():
    nettoyer()
 
    conteneur = tk.Frame(fenetre, bg=FOND)
    conteneur.pack(fill="both", expand=True)
 
    menu_lateral(conteneur)
 
    principal = tk.Frame(conteneur, bg=FOND)
    principal.pack(side="right", fill="both", expand=True)
 
    titre_page(principal, "Gestion des produits")
 
    barre = tk.Frame(principal, bg=FOND)
    barre.pack(fill="x", padx=28)
 
    tk.Label(
        barre,
        text="Rechercher :",
        bg=FOND,
        fg=TEXTE,
        font=("Arial", 10, "bold")
    ).pack(side="left")
 
    recherche = champ(barre, 35)
    recherche.pack(side="left", padx=10, ipady=5)
 
    tree = ttk.Treeview(
        principal,
        columns=(
            "code",
            "nom",
            "categorie",
            "prix",
            "quantite",
            "fournisseur"
        ),
        show="headings"
    )
 
    colonnes = [
        ("code", "CODE", 100),
        ("nom", "PRODUIT", 180),
        ("categorie", "CATEGORIE", 130),
        ("prix", "PRIX", 130),
        ("quantite", "STOCK", 80),
        ("fournisseur", "FOURNISSEUR", 150)
    ]
 
    for col, texte, largeur in colonnes:
        tree.heading(col, text=texte)
        tree.column(col, width=largeur, anchor="center")
 
    tree.tag_configure("faible", background=ROUGE_CLAIR)
 
    tree.pack(
        fill="both",
        expand=True,
        padx=28,
        pady=15
    )
 
    recherche.bind(
        "<KeyRelease>",
        lambda e: actualiser_produits(
            tree,
            recherche.get()
        )
    )
 
    zone = tk.Frame(principal, bg=FOND)
    zone.pack(pady=(0, 20))
 
    if role_connecte == "Administrateur":
        bouton(
            zone, "AJOUTER",
            lambda: formulaire_produit(tree),
            VERT, 15
        ).pack(side="left", padx=5)
 
        bouton(
            zone, "MODIFIER",
            lambda: modifier_produit(tree),
            BLEU, 15
        ).pack(side="left", padx=5)
 
        bouton(
            zone, "SUPPRIMER",
            lambda: supprimer_produit(tree),
            ROUGE, 15
        ).pack(side="left", padx=5)
 
    bouton(
        zone, "RETOUR",
        retour_dashboard, GRIS, 15
    ).pack(side="left", padx=5)
 
    actualiser_produits(tree)
 
 
def formulaire_produit(tree, produit=None):
    fen = tk.Toplevel(fenetre)
    fen.title("Produit")
    fen.geometry("430x560")
    fen.configure(bg=BLANC)
    fen.resizable(False, False)
 
    tk.Label(
        fen,
        text="Nouveau produit" if produit is None
        else "Modifier le produit",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 18, "bold")
    ).pack(pady=20)
 
    labels = [
        "Code",
        "Nom",
        "Categorie",
        "Prix",
        "Quantite",
        "Fournisseur"
    ]
 
    entrees = []
 
    for label in labels:
        tk.Label(
            fen,
            text=label,
            bg=BLANC,
            fg=TEXTE,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=45, pady=(6, 3))
 
        e = champ(fen, 38)
        e.pack(padx=45, ipady=5)
 
        entrees.append(e)
 
    if produit:
        for i, valeur in enumerate(produit):
            entrees[i].insert(
                0,
                str(valeur if valeur is not None else "")
            )
 
    def enregistrer():
        try:
            code = entrees[0].get().strip()
            nom = entrees[1].get().strip()
            categorie = entrees[2].get().strip()
            prix = float(entrees[3].get())
            quantite = int(entrees[4].get())
            fournisseur = entrees[5].get().strip()
 
            if code == "" or nom == "":
                messagebox.showwarning(
                    "Produit",
                    "Le code et le nom sont obligatoires."
                )
                return
 
            if prix < 0 or quantite < 0:
                messagebox.showwarning(
                    "Produit",
                    "Prix et quantite doivent etre positifs."
                )
                return
 
            if produit is None:
                executer("""
                    INSERT INTO produits
                    (code, nom, categorie, prix, quantite, fournisseur)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    code,
                    nom,
                    categorie,
                    prix,
                    quantite,
                    fournisseur
                ))
            else:
                executer("""
                    UPDATE produits
                    SET code=?,
                        nom=?,
                        categorie=?,
                        prix=?,
                        quantite=?,
                        fournisseur=?
                    WHERE code=?
                """, (
                    code,
                    nom,
                    categorie,
                    prix,
                    quantite,
                    fournisseur,
                    produit[0]
                ))
 
            actualiser_produits(tree)
            fen.destroy()
 
            messagebox.showinfo(
                "Produit",
                "Produit enregistre avec succes."
            )
 
        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Prix ou quantite incorrect."
            )
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Erreur",
                "Ce code produit existe deja."
            )
 
    bouton(
        fen,
        "ENREGISTRER",
        enregistrer,
        VERT,
        22
    ).pack(pady=22)
 
 
def modifier_produit(tree):
    selection = tree.selection()
 
    if not selection:
        messagebox.showwarning(
            "Produit",
            "Selectionnez un produit."
        )
        return
 
    valeurs = tree.item(
        selection[0],
        "values"
    )
 
    prix = (
        str(valeurs[3])
        .replace(" GNF", "")
        .replace(" ", "")
    )
 
    produit = (
        valeurs[0],
        valeurs[1],
        valeurs[2],
        prix,
        valeurs[4],
        valeurs[5]
    )
 
    formulaire_produit(tree, produit)
 
 
def supprimer_produit(tree):
    selection = tree.selection()
 
    if not selection:
        messagebox.showwarning(
            "Produit",
            "Selectionnez un produit."
        )
        return
 
    code = tree.item(
        selection[0],
        "values"
    )[0]
 
    if messagebox.askyesno(
        "Confirmation",
        "Supprimer ce produit ?"
    ):
        executer(
            "DELETE FROM produits WHERE code=?",
            (code,)
        )
 
        actualiser_produits(tree)
 
        messagebox.showinfo(
            "Produit",
            "Produit supprime."
        )
 
 
# ============================================================
# STOCK
# ============================================================
 
def ouvrir_stock():
    nettoyer()
 
    conteneur = tk.Frame(fenetre, bg=FOND)
    conteneur.pack(fill="both", expand=True)
 
    menu_lateral(conteneur)
 
    principal = tk.Frame(conteneur, bg=FOND)
    principal.pack(side="right", fill="both", expand=True)
 
    titre_page(principal, "Gestion du stock")
 
    tk.Label(
        principal,
        text=f"Seuil d'alerte : {SEUIL_STOCK} unites",
        bg=ORANGE_CLAIR,
        fg="#92400E",
        font=("Arial", 10, "bold"),
        padx=15,
        pady=10
    ).pack(fill="x", padx=28)
 
    tree = ttk.Treeview(
        principal,
        columns=("code", "nom", "stock", "prix"),
        show="headings"
    )
 
    for col, texte, largeur in [
        ("code", "CODE", 140),
        ("nom", "PRODUIT", 300),
        ("stock", "STOCK", 150),
        ("prix", "PRIX", 180)
    ]:
        tree.heading(col, text=texte)
        tree.column(col, width=largeur, anchor="center")
 
    tree.tag_configure(
        "faible",
        background=ROUGE_CLAIR
    )
 
    tree.pack(
        fill="both",
        expand=True,
        padx=28,
        pady=15
    )
 
    produits = executer("""
        SELECT code, nom, quantite, prix
        FROM produits
        ORDER BY nom
    """)
 
    for p in produits:
        tag = "faible" if p[2] <= SEUIL_STOCK else ""
 
        tree.insert(
            "",
            "end",
            values=(
                p[0],
                p[1],
                p[2],
                format_prix(p[3])
            ),
            tags=(tag,)
        )
 
    zone = tk.Frame(principal, bg=FOND)
    zone.pack(pady=(0, 20))
 
    if role_connecte == "Administrateur":
        bouton(
            zone,
            "MODIFIER STOCK",
            lambda: modifier_stock(tree),
            ORANGE,
            18
        ).pack(side="left", padx=5)
 
    bouton(
        zone,
        "RETOUR",
        retour_dashboard,
        GRIS,
        15
    ).pack(side="left", padx=5)
 
 
def modifier_stock(tree):
    selection = tree.selection()
 
    if not selection:
        messagebox.showwarning(
            "Stock",
            "Selectionnez un produit."
        )
        return
 
    valeurs = tree.item(
        selection[0],
        "values"
    )
 
    code = valeurs[0]
 
    fen = tk.Toplevel(fenetre)
    fen.title("Modifier le stock")
    fen.geometry("350x230")
    fen.configure(bg=BLANC)
    fen.resizable(False, False)
 
    tk.Label(
        fen,
        text="Nouvelle quantite",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 13, "bold")
    ).pack(pady=25)
 
    entree = champ(fen, 20)
    entree.pack(ipady=6)
    entree.insert(0, valeurs[2])
 
    def valider():
        try:
            qte = int(entree.get())
 
            if qte < 0:
                raise ValueError
 
            executer(
                "UPDATE produits SET quantite=? WHERE code=?",
                (qte, code)
            )
 
            fen.destroy()
            ouvrir_stock()
 
        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Entrez une quantite valide."
            )
 
    bouton(
        fen,
        "VALIDER",
        valider,
        ORANGE,
        18
    ).pack(pady=20)
 
 
# ============================================================
# FOURNISSEURS
# ============================================================
 
def ouvrir_fournisseurs():
    nettoyer()
 
    conteneur = tk.Frame(fenetre, bg=FOND)
    conteneur.pack(fill="both", expand=True)
 
    menu_lateral(conteneur)
 
    principal = tk.Frame(conteneur, bg=FOND)
    principal.pack(side="right", fill="both", expand=True)
 
    titre_page(principal, "Gestion des fournisseurs")
 
    tree = ttk.Treeview(
        principal,
        columns=("id", "nom", "telephone", "email"),
        show="headings"
    )
 
    for col, texte, largeur in [
        ("id", "ID", 70),
        ("nom", "NOM", 250),
        ("telephone", "TELEPHONE", 180),
        ("email", "EMAIL", 250)
    ]:
        tree.heading(col, text=texte)
        tree.column(col, width=largeur, anchor="center")
 
    tree.pack(
        fill="both",
        expand=True,
        padx=28,
        pady=15
    )
 
    actualiser_fournisseurs(tree)
 
    zone = tk.Frame(principal, bg=FOND)
    zone.pack(pady=(0, 20))
 
    bouton(
        zone,
        "AJOUTER",
        lambda: formulaire_fournisseur(tree),
        VERT,
        15
    ).pack(side="left", padx=5)
 
    bouton(
        zone,
        "SUPPRIMER",
        lambda: supprimer_fournisseur(tree),
        ROUGE,
        15
    ).pack(side="left", padx=5)
 
    bouton(
        zone,
        "RETOUR",
        retour_dashboard,
        GRIS,
        15
    ).pack(side="left", padx=5)
 
 
def actualiser_fournisseurs(tree):
    for ligne in tree.get_children():
        tree.delete(ligne)
 
    fournisseurs = executer("""
        SELECT id, nom, telephone, email
        FROM fournisseurs
        ORDER BY id DESC
    """)
 
    for f in fournisseurs:
        tree.insert("", "end", values=f)
 
 
def formulaire_fournisseur(tree):
    fen = tk.Toplevel(fenetre)
    fen.title("Ajouter un fournisseur")
    fen.geometry("400x350")
    fen.configure(bg=BLANC)
 
    champs = []
 
    for texte in [
        "Nom",
        "Telephone",
        "Email"
    ]:
        tk.Label(
            fen,
            text=texte,
            bg=BLANC,
            fg=TEXTE,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=40, pady=(15, 3))
 
        e = champ(fen, 30)
        e.pack(padx=40, ipady=5)
        champs.append(e)
 
    def enregistrer():
        nom = champs[0].get().strip()
 
        if nom == "":
            messagebox.showwarning(
                "Fournisseur",
                "Le nom est obligatoire."
            )
            return
 
        executer("""
            INSERT INTO fournisseurs
            (nom, telephone, email)
            VALUES (?, ?, ?)
        """, (
            nom,
            champs[1].get().strip(),
            champs[2].get().strip()
        ))
 
        fen.destroy()
        actualiser_fournisseurs(tree)
 
    bouton(
        fen,
        "ENREGISTRER",
        enregistrer,
        VERT,
        20
    ).pack(pady=20)
 
 
def supprimer_fournisseur(tree):
    selection = tree.selection()
 
    if not selection:
        messagebox.showwarning(
            "Fournisseur",
            "Selectionnez un fournisseur."
        )
        return
 
    identifiant = tree.item(
        selection[0],
        "values"
    )[0]
 
    if messagebox.askyesno(
        "Confirmation",
        "Supprimer ce fournisseur ?"
    ):
        executer(
            "DELETE FROM fournisseurs WHERE id=?",
            (identifiant,)
        )
 
        actualiser_fournisseurs(tree)
 
 
# ============================================================
# CLIENTS
# ============================================================
 
def ouvrir_clients():
    nettoyer()
 
    conteneur = tk.Frame(fenetre, bg=FOND)
    conteneur.pack(fill="both", expand=True)
 
    menu_lateral(conteneur)
 
    principal = tk.Frame(conteneur, bg=FOND)
    principal.pack(side="right", fill="both", expand=True)
 
    titre_page(principal, "Gestion des clients")
 
    tree = ttk.Treeview(
        principal,
        columns=("id", "nom", "telephone", "email"),
        show="headings"
    )
 
    for col, texte, largeur in [
        ("id", "ID", 70),
        ("nom", "NOM", 250),
        ("telephone", "TELEPHONE", 180),
        ("email", "EMAIL", 250)
    ]:
        tree.heading(col, text=texte)
        tree.column(col, width=largeur, anchor="center")
 
    tree.pack(
        fill="both",
        expand=True,
        padx=28,
        pady=15
    )
 
    actualiser_clients(tree)
 
    zone = tk.Frame(principal, bg=FOND)
    zone.pack(pady=(0, 20))
 
    bouton(
        zone,
        "AJOUTER",
        lambda: formulaire_client(tree),
        VERT,
        15
    ).pack(side="left", padx=5)
 
    bouton(
        zone,
        "SUPPRIMER",
        lambda: supprimer_client(tree),
        ROUGE,
        15
    ).pack(side="left", padx=5)
 
    bouton(
        zone,
        "RETOUR",
        retour_dashboard,
        GRIS,
        15
    ).pack(side="left", padx=5)
 
 
def actualiser_clients(tree):
    for ligne in tree.get_children():
        tree.delete(ligne)
 
    clients = executer("""
        SELECT id, nom, telephone, email
        FROM clients
        ORDER BY id DESC
    """)
 
    for c in clients:
        tree.insert("", "end", values=c)
 
 
def formulaire_client(tree):
    fen = tk.Toplevel(fenetre)
    fen.title("Ajouter un client")
    fen.geometry("400x350")
    fen.configure(bg=BLANC)
 
    champs = []
 
    for texte in [
        "Nom",
        "Telephone",
        "Email"
    ]:
        tk.Label(
            fen,
            text=texte,
            bg=BLANC,
            fg=TEXTE,
            font=("Arial", 10, "bold")
        ).pack(anchor="w", padx=40, pady=(15, 3))
 
        e = champ(fen, 30)
        e.pack(padx=40, ipady=5)
        champs.append(e)
 
    def enregistrer():
        nom = champs[0].get().strip()
 
        if nom == "":
            messagebox.showwarning(
                "Client",
                "Le nom est obligatoire."
            )
            return
 
        executer("""
            INSERT INTO clients
            (nom, telephone, email)
            VALUES (?, ?, ?)
        """, (
            nom,
            champs[1].get().strip(),
            champs[2].get().strip()
        ))
 
        fen.destroy()
        actualiser_clients(tree)
 
    bouton(
        fen,
        "ENREGISTRER",
        enregistrer,
        VERT,
        20
    ).pack(pady=20)
 
 
def supprimer_client(tree):
    selection = tree.selection()
 
    if not selection:
        messagebox.showwarning(
            "Client",
            "Selectionnez un client."
        )
        return
 
    identifiant = tree.item(
        selection[0],
        "values"
    )[0]
 
    if messagebox.askyesno(
        "Confirmation",
        "Supprimer ce client ?"
    ):
        executer(
            "DELETE FROM clients WHERE id=?",
            (identifiant,)
        )
 
        actualiser_clients(tree)
 
 
# ============================================================
# CAISSE
# ============================================================
 
def ouvrir_caisse():
    global panier
 
    panier = []
 
    nettoyer()
 
    conteneur = tk.Frame(fenetre, bg=FOND)
    conteneur.pack(fill="both", expand=True)
 
    menu_lateral(conteneur)
 
    principal = tk.Frame(conteneur, bg=FOND)
    principal.pack(side="right", fill="both", expand=True)
 
    titre_page(principal, "Caisse - Nouvelle vente")
 
    gauche = tk.Frame(
        principal,
        bg=BLANC,
        highlightbackground=BORDURE,
        highlightthickness=1
    )
    gauche.pack(
        side="left",
        fill="both",
        expand=True,
        padx=(28, 10),
        pady=(0, 25)
    )
 
    droite = tk.Frame(
        principal,
        bg=BLANC,
        width=350,
        highlightbackground=BORDURE,
        highlightthickness=1
    )
    droite.pack(
        side="right",
        fill="y",
        padx=(10, 28),
        pady=(0, 25)
    )
    droite.pack_propagate(False)
 
    tk.Label(
        gauche,
        text="Ajouter au panier",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 14, "bold")
    ).pack(anchor="w", padx=18, pady=(18, 10))
 
    zone_recherche = tk.Frame(
        gauche,
        bg=BLANC
    )
    zone_recherche.pack(fill="x", padx=18)
 
    tk.Label(
        zone_recherche,
        text="Code produit :",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 10, "bold")
    ).pack(side="left")
 
    entree_code = champ(zone_recherche, 20)
    entree_code.pack(
        side="left",
        padx=10,
        ipady=5
    )
 
    entree_qte = champ(zone_recherche, 7)
    entree_qte.insert(0, "1")
    entree_qte.pack(
        side="left",
        padx=5,
        ipady=5
    )
 
    tree_produits = ttk.Treeview(
        gauche,
        columns=("code", "nom", "prix", "stock"),
        show="headings",
        height=9
    )
 
    for col, texte, largeur in [
        ("code", "CODE", 90),
        ("nom", "PRODUIT", 190),
        ("prix", "PRIX", 120),
        ("stock", "STOCK", 80)
    ]:
        tree_produits.heading(
            col,
            text=texte
        )
        tree_produits.column(
            col,
            width=largeur,
            anchor="center"
        )
 
    tree_produits.pack(
        fill="x",
        padx=18,
        pady=12
    )
 
    produits = executer("""
        SELECT code, nom, prix, quantite
        FROM produits
        ORDER BY nom
    """)
 
    for p in produits:
        tree_produits.insert(
            "",
            "end",
            values=(
                p[0],
                p[1],
                format_prix(p[2]),
                p[3]
            )
        )
 
    tree_panier = ttk.Treeview(
        gauche,
        columns=(
            "code",
            "nom",
            "qte",
            "prix",
            "total"
        ),
        show="headings"
    )
 
    for col, texte, largeur in [
        ("code", "CODE", 80),
        ("nom", "PRODUIT", 150),
        ("qte", "QTE", 60),
        ("prix", "PRIX", 100),
        ("total", "TOTAL", 120)
    ]:
        tree_panier.heading(
            col,
            text=texte
        )
        tree_panier.column(
            col,
            width=largeur,
            anchor="center"
        )
 
    tree_panier.pack(
        fill="both",
        expand=True,
        padx=18,
        pady=(5, 12)
    )
 
    tk.Label(
        droite,
        text="TOTAL A PAYER",
        bg=BLANC,
        fg=GRIS,
        font=("Arial", 11, "bold")
    ).pack(pady=(35, 2))
 
    label_total = tk.Label(
        droite,
        text="0 GNF",
        bg=BLANC,
        fg=VERT,
        font=("Arial", 28, "bold")
    )
    label_total.pack(pady=(0, 25))
 
    tk.Label(
        droite,
        text="Client (facultatif)",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", padx=25)
 
    entree_client = champ(droite, 28)
    entree_client.pack(
        padx=25,
        pady=(6, 15),
        ipady=5
    )
 
    tk.Label(
        droite,
        text="Montant recu",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", padx=25)
 
    entree_paiement = champ(droite, 28)
    entree_paiement.pack(
        padx=25,
        pady=(6, 20),
        ipady=5
    )
 
    label_monnaie = tk.Label(
        droite,
        text="Monnaie : 0 GNF",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 12, "bold")
    )
    label_monnaie.pack(pady=5)
 
    def recalculer():
        total = 0
 
        for ligne in panier:
            total += ligne["total"]
 
        label_total.config(
            text=format_prix(total)
        )
 
        try:
            paiement = float(
                entree_paiement.get()
            )
 
            monnaie = paiement - total
 
            label_monnaie.config(
                text="Monnaie : " +
                format_prix(max(monnaie, 0))
            )
        except:
            label_monnaie.config(
                text="Monnaie : 0 GNF"
            )
 
    def afficher_panier():
        for ligne in tree_panier.get_children():
            tree_panier.delete(ligne)
 
        for ligne in panier:
            tree_panier.insert(
                "",
                "end",
                values=(
                    ligne["code"],
                    ligne["nom"],
                    ligne["quantite"],
                    format_prix(ligne["prix"]),
                    format_prix(ligne["total"])
                )
            )
 
        recalculer()
 
    def ajouter():
        code = entree_code.get().strip()
 
        try:
            qte = int(
                entree_qte.get()
            )
        except:
            messagebox.showerror(
                "Caisse",
                "Quantite incorrecte."
            )
            return
 
        if qte <= 0:
            messagebox.showwarning(
                "Caisse",
                "La quantite doit etre positive."
            )
            return
 
        produit = obtenir_produit(code)
 
        if produit is None:
            messagebox.showerror(
                "Caisse",
                "Produit introuvable."
            )
            return
 
        _, code, nom, categorie, prix, stock, fournisseur = produit
 
        deja = 0
 
        for ligne in panier:
            if ligne["code"] == code:
                deja = ligne["quantite"]
 
        if deja + qte > stock:
            messagebox.showwarning(
                "Stock",
                "Stock insuffisant."
            )
            return
 
        trouve = False
 
        for ligne in panier:
            if ligne["code"] == code:
                ligne["quantite"] += qte
                ligne["total"] = (
                    ligne["quantite"] *
                    ligne["prix"]
                )
                trouve = True
 
        if not trouve:
            panier.append({
                "code": code,
                "nom": nom,
                "quantite": qte,
                "prix": prix,
                "total": qte * prix
            })
 
        afficher_panier()
 
        entree_code.delete(0, "end")
        entree_qte.delete(0, "end")
        entree_qte.insert(0, "1")
 
    def supprimer_panier():
        selection = tree_panier.selection()
 
        if not selection:
            messagebox.showwarning(
                "Caisse",
                "Selectionnez une ligne du panier."
            )
            return
 
        code = tree_panier.item(
            selection[0],
            "values"
        )[0]
 
        for ligne in panier:
            if ligne["code"] == code:
                panier.remove(ligne)
                break
 
        afficher_panier()
 
    def valider():
        if len(panier) == 0:
            messagebox.showwarning(
                "Caisse",
                "Le panier est vide."
            )
            return
 
        total = 0
 
        for ligne in panier:
            total += ligne["total"]
 
        try:
            paiement = float(
                entree_paiement.get()
            )
        except:
            messagebox.showerror(
                "Paiement",
                "Montant recu incorrect."
            )
            return
 
        if paiement < total:
            messagebox.showwarning(
                "Paiement",
                "Le montant recu est insuffisant."
            )
            return
 
        monnaie = paiement - total
        numero = prochain_numero()
        date = datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S"
        )
 
        db = connexion_db()
        c = db.cursor()
 
        try:
            c.execute("""
                INSERT INTO ventes
                (numero, vendeur, client, total,
                 paiement, monnaie, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                numero,
                utilisateur_connecte,
                entree_client.get().strip(),
                total,
                paiement,
                monnaie,
                date
            ))
 
            vente_id = c.lastrowid
 
            for ligne in panier:
                c.execute("""
                    INSERT INTO lignes_vente
                    (vente_id, code_produit,
                     nom_produit, quantite,
                     prix_unitaire, total)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    vente_id,
                    ligne["code"],
                    ligne["nom"],
                    ligne["quantite"],
                    ligne["prix"],
                    ligne["total"]
                ))
 
                c.execute("""
                    UPDATE produits
                    SET quantite = quantite - ?
                    WHERE code=?
                """, (
                    ligne["quantite"],
                    ligne["code"]
                ))
 
            db.commit()
            db.close()
 
            generer_facture(
                numero,
                date,
                entree_client.get().strip(),
                total,
                paiement,
                monnaie,
                panier
            )
 
            messagebox.showinfo(
                "Vente enregistree",
                f"Vente {numero} enregistree avec succes.\n\n"
                f"Total : {format_prix(total)}\n"
                f"Monnaie : {format_prix(monnaie)}"
            )
 
            panier.clear()
            ouvrir_caisse()
 
        except Exception as erreur:
            db.rollback()
            db.close()
 
            messagebox.showerror(
                "Erreur",
                str(erreur)
            )
 
    bouton(
        zone_recherche,
        "AJOUTER",
        ajouter,
        BLEU,
        12
    ).pack(side="left", padx=5)
 
    bouton(
        gauche,
        "RETIRER DU PANIER",
        supprimer_panier,
        ROUGE,
        20
    ).pack(
        side="left",
        padx=18,
        pady=(0, 15)
    )
 
    bouton(
        droite,
        "VALIDER LA VENTE",
        valider,
        VERT,
        25
    ).pack(pady=20)
 
    bouton(
        droite,
        "RETOUR",
        retour_dashboard,
        GRIS,
        25
    ).pack()
 
    entree_paiement.bind(
        "<KeyRelease>",
        lambda e: recalculer()
    )
 
    entree_code.bind(
        "<Return>",
        lambda e: ajouter()
    )
 
 
# ============================================================
# FACTURES
# ============================================================
 
def generer_facture(
    numero,
    date,
    client,
    total,
    paiement,
    monnaie,
    lignes
):
    dossier = "factures"
 
    if not os.path.exists(dossier):
        os.makedirs(dossier)
 
    nom_fichier = os.path.join(
        dossier,
        f"facture_{numero}.txt"
    )
 
    texte = ""
    texte += "========================================\n"
    texte += "             SUPERMARCHE PRO\n"
    texte += "========================================\n"
    texte += f"Facture : {numero}\n"
    texte += f"Date    : {date}\n"
    texte += f"Vendeur : {utilisateur_connecte}\n"
    texte += (
        f"Client  : {client if client else 'Client comptoir'}\n"
    )
    texte += "----------------------------------------\n"
 
    for ligne in lignes:
        texte += f"{ligne['nom']}\n"
        texte += (
            f"  {ligne['quantite']} x "
            f"{format_prix(ligne['prix'])}"
            f" = {format_prix(ligne['total'])}\n"
        )
 
    texte += "----------------------------------------\n"
    texte += f"TOTAL    : {format_prix(total)}\n"
    texte += f"RECU     : {format_prix(paiement)}\n"
    texte += f"MONNAIE  : {format_prix(monnaie)}\n"
    texte += "========================================\n"
    texte += "         Merci pour votre achat !\n"
    texte += "========================================\n"
 
    f = open(
        nom_fichier,
        "w",
        encoding="utf-8"
    )
 
    f.write(texte)
    f.close()
 
 
def afficher_texte(titre, texte):
    fen = tk.Toplevel(fenetre)
    fen.title(titre)
    fen.geometry("600x650")
    fen.configure(bg=BLANC)
 
    zone = tk.Text(
        fen,
        font=("Courier New", 10),
        bg=BLANC,
        fg=TEXTE,
        padx=20,
        pady=20
    )
 
    zone.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=20
    )
 
    zone.insert("1.0", texte)
    zone.config(state="disabled")
 
 
# ============================================================
# HISTORIQUE DES VENTES
# ============================================================
 
def ouvrir_ventes():
    nettoyer()
 
    conteneur = tk.Frame(fenetre, bg=FOND)
    conteneur.pack(fill="both", expand=True)
 
    menu_lateral(conteneur)
 
    principal = tk.Frame(conteneur, bg=FOND)
    principal.pack(side="right", fill="both", expand=True)
 
    titre_page(principal, "Historique des ventes")
 
    if role_connecte == "Administrateur":
        ventes = executer("""
            SELECT numero, vendeur, client,
                   total, paiement, monnaie, date
            FROM ventes
            ORDER BY id DESC
        """)
    else:
        ventes = executer("""
            SELECT numero, vendeur, client,
                   total, paiement, monnaie, date
            FROM ventes
            WHERE vendeur=?
            ORDER BY id DESC
        """, (utilisateur_connecte,))
 
    tree = ttk.Treeview(
        principal,
        columns=(
            "numero",
            "vendeur",
            "client",
            "total",
            "paiement",
            "monnaie",
            "date"
        ),
        show="headings"
    )
 
    for col, texte, largeur in [
        ("numero", "FACTURE", 120),
        ("vendeur", "VENDEUR", 100),
        ("client", "CLIENT", 130),
        ("total", "TOTAL", 120),
        ("paiement", "RECU", 120),
        ("monnaie", "MONNAIE", 120),
        ("date", "DATE", 160)
    ]:
        tree.heading(
            col,
            text=texte
        )
        tree.column(
            col,
            width=largeur,
            anchor="center"
        )
 
    tree.pack(
        fill="both",
        expand=True,
        padx=28,
        pady=15
    )
 
    for v in ventes:
        tree.insert(
            "",
            "end",
            values=(
                v[0],
                v[1],
                v[2] or "-",
                format_prix(v[3]),
                format_prix(v[4]),
                format_prix(v[5]),
                v[6]
            )
        )
 
    zone = tk.Frame(
        principal,
        bg=FOND
    )
    zone.pack(pady=(0, 20))
 
    bouton(
        zone,
        "AFFICHER FACTURE",
        lambda: afficher_facture_selection(tree),
        BLEU,
        20
    ).pack(side="left", padx=5)
 
    bouton(
        zone,
        "RETOUR",
        retour_dashboard,
        GRIS,
        15
    ).pack(side="left", padx=5)
 
 
def afficher_facture_selection(tree):
    selection = tree.selection()
 
    if not selection:
        messagebox.showwarning(
            "Vente",
            "Selectionnez une vente."
        )
        return
 
    numero = tree.item(
        selection[0],
        "values"
    )[0]
 
    vente = executer("""
        SELECT numero, vendeur, client,
               total, paiement, monnaie, date
        FROM ventes
        WHERE numero=?
    """, (numero,))
 
    lignes = executer("""
        SELECT nom_produit,
               quantite,
               prix_unitaire,
               total
        FROM lignes_vente
        JOIN ventes
        ON lignes_vente.vente_id = ventes.id
        WHERE ventes.numero=?
    """, (numero,))
 
    if not vente:
        return
 
    v = vente[0]
 
    texte = ""
    texte += "========================================\n"
    texte += "             SUPERMARCHE PRO\n"
    texte += "========================================\n"
    texte += f"Facture : {v[0]}\n"
    texte += f"Date    : {v[6]}\n"
    texte += f"Vendeur : {v[1]}\n"
    texte += (
        f"Client  : {v[2] or 'Client comptoir'}\n"
    )
    texte += "----------------------------------------\n"
 
    for ligne in lignes:
        texte += (
            f"{ligne[0]} - {ligne[1]} x "
            f"{format_prix(ligne[2])}\n"
        )
        texte += (
            f"Total ligne : "
            f"{format_prix(ligne[3])}\n"
        )
 
    texte += "----------------------------------------\n"
    texte += f"TOTAL   : {format_prix(v[3])}\n"
    texte += f"RECU    : {format_prix(v[4])}\n"
    texte += f"MONNAIE : {format_prix(v[5])}\n"
    texte += "========================================\n"
    texte += "        Merci pour votre achat !\n"
    texte += "========================================\n"
 
    afficher_texte(
        "Facture " + numero,
        texte
    )
 
 
# ============================================================
# STATISTIQUES
# ============================================================
 
def ouvrir_statistiques():
    nettoyer()
 
    conteneur = tk.Frame(fenetre, bg=FOND)
    conteneur.pack(fill="both", expand=True)
 
    menu_lateral(conteneur)
 
    principal = tk.Frame(conteneur, bg=FOND)
    principal.pack(side="right", fill="both", expand=True)
 
    titre_page(
        principal,
        "Statistiques et rapports"
    )
 
    cartes = tk.Frame(
        principal,
        bg=FOND
    )
    cartes.pack(
        fill="x",
        padx=18
    )
 
    for i in range(3):
        cartes.grid_columnconfigure(
            i,
            weight=1
        )
 
    carte_stat(
        cartes,
        "NOMBRE DE VENTES",
        str(nombre_ventes()),
        BLEU,
        0,
        0
    )
 
    carte_stat(
        cartes,
        "CHIFFRE D'AFFAIRES",
        format_prix(chiffre_affaires()),
        VERT,
        0,
        1
    )
 
    carte_stat(
        cartes,
        "STOCK TOTAL",
        str(total_stock()),
        ORANGE,
        0,
        2
    )
 
    zone = tk.Frame(
        principal,
        bg=BLANC,
        highlightbackground=BORDURE,
        highlightthickness=1
    )
    zone.pack(
        fill="both",
        expand=True,
        padx=28,
        pady=20
    )
 
    tk.Label(
        zone,
        text="Produits les plus vendus",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 15, "bold")
    ).pack(
        anchor="w",
        padx=20,
        pady=20
    )
 
    tree = ttk.Treeview(
        zone,
        columns=("produit", "quantite", "ca"),
        show="headings"
    )
 
    for col, texte, largeur in [
        ("produit", "PRODUIT", 300),
        ("quantite", "QUANTITE VENDUE", 180),
        ("ca", "CHIFFRE D'AFFAIRES", 200)
    ]:
        tree.heading(
            col,
            text=texte
        )
        tree.column(
            col,
            width=largeur,
            anchor="center"
        )
 
    tree.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 20)
    )
 
    resultat = executer("""
        SELECT nom_produit,
               SUM(quantite),
               SUM(total)
        FROM lignes_vente
        GROUP BY nom_produit
        ORDER BY SUM(quantite) DESC
        LIMIT 10
    """)
 
    for ligne in resultat:
        tree.insert(
            "",
            "end",
            values=(
                ligne[0],
                ligne[1],
                format_prix(ligne[2])
            )
        )
 
    bouton(
        principal,
        "RETOUR",
        retour_dashboard,
        GRIS,
        15
    ).pack(pady=(0, 20))
 
 
# ============================================================
# ALERTES STOCK
# ============================================================
 
def ouvrir_alertes():
    nettoyer()
 
    conteneur = tk.Frame(fenetre, bg=FOND)
    conteneur.pack(fill="both", expand=True)
 
    menu_lateral(conteneur)
 
    principal = tk.Frame(conteneur, bg=FOND)
    principal.pack(side="right", fill="both", expand=True)
 
    titre_page(
        principal,
        "Alertes de stock"
    )
 
    faibles = executer("""
        SELECT code, nom, quantite, prix
        FROM produits
        WHERE quantite <= ?
        ORDER BY quantite ASC
    """, (SEUIL_STOCK,))
 
    if len(faibles) == 0:
        tk.Label(
            principal,
            text="Aucune alerte de stock.",
            bg=VERT_CLAIR,
            fg=VERT,
            font=("Arial", 14, "bold"),
            padx=25,
            pady=25
        ).pack(
            fill="x",
            padx=28,
            pady=15
        )
    else:
        tk.Label(
            principal,
            text=(
                f"{len(faibles)} produit(s) "
                "ont un stock faible."
            ),
            bg=ROUGE_CLAIR,
            fg=ROUGE,
            font=("Arial", 13, "bold"),
            padx=20,
            pady=18
        ).pack(
            fill="x",
            padx=28,
            pady=(0, 15)
        )
 
        tree = ttk.Treeview(
            principal,
            columns=(
                "code",
                "nom",
                "stock",
                "prix"
            ),
            show="headings"
        )
 
        for col, texte, largeur in [
            ("code", "CODE", 130),
            ("nom", "PRODUIT", 300),
            ("stock", "STOCK", 130),
            ("prix", "PRIX", 170)
        ]:
            tree.heading(
                col,
                text=texte
            )
            tree.column(
                col,
                width=largeur,
                anchor="center"
            )
 
        tree.pack(
            fill="both",
            expand=True,
            padx=28,
            pady=10
        )
 
        for p in faibles:
            tree.insert(
                "",
                "end",
                values=(
                    p[0],
                    p[1],
                    p[2],
                    format_prix(p[3])
                )
            )
 
    bouton(
        principal,
        "RETOUR",
        retour_dashboard,
        GRIS,
        15
    ).pack(pady=20)
 
 
# ============================================================
# UTILISATEURS
# ============================================================
 
def ouvrir_utilisateurs():
    nettoyer()
 
    conteneur = tk.Frame(fenetre, bg=FOND)
    conteneur.pack(fill="both", expand=True)
 
    menu_lateral(conteneur)
 
    principal = tk.Frame(conteneur, bg=FOND)
    principal.pack(side="right", fill="both", expand=True)
 
    titre_page(
        principal,
        "Gestion des utilisateurs"
    )
 
    tree = ttk.Treeview(
        principal,
        columns=("id", "nom", "role"),
        show="headings"
    )
 
    for col, texte, largeur in [
        ("id", "ID", 80),
        ("nom", "UTILISATEUR", 250),
        ("role", "ROLE", 250)
    ]:
        tree.heading(
            col,
            text=texte
        )
        tree.column(
            col,
            width=largeur,
            anchor="center"
        )
 
    tree.pack(
        fill="both",
        expand=True,
        padx=28,
        pady=15
    )
 
    actualiser_utilisateurs(tree)
 
    zone = tk.Frame(
        principal,
        bg=FOND
    )
    zone.pack(pady=(0, 20))
 
    bouton(
        zone,
        "AJOUTER",
        lambda: formulaire_utilisateur(tree),
        VERT,
        15
    ).pack(side="left", padx=5)
 
    bouton(
        zone,
        "SUPPRIMER",
        lambda: supprimer_utilisateur(tree),
        ROUGE,
        15
    ).pack(side="left", padx=5)
 
    bouton(
        zone,
        "RETOUR",
        retour_dashboard,
        GRIS,
        15
    ).pack(side="left", padx=5)
 
 
def actualiser_utilisateurs(tree):
    for ligne in tree.get_children():
        tree.delete(ligne)
 
    utilisateurs = executer("""
        SELECT id, nom, role
        FROM utilisateurs
        ORDER BY id
    """)
 
    for u in utilisateurs:
        tree.insert(
            "",
            "end",
            values=u
        )
 
 
def formulaire_utilisateur(tree):
    fen = tk.Toplevel(fenetre)
    fen.title("Ajouter un utilisateur")
    fen.geometry("400x380")
    fen.configure(bg=BLANC)
    fen.resizable(False, False)
 
    tk.Label(
        fen,
        text="Nouvel utilisateur",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 18, "bold")
    ).pack(pady=20)
 
    tk.Label(
        fen,
        text="Nom",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", padx=40)
 
    nom = champ(fen, 30)
    nom.pack(
        padx=40,
        pady=(5, 15),
        ipady=5
    )
 
    tk.Label(
        fen,
        text="Mot de passe",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", padx=40)
 
    mdp = champ(fen, 30)
    mdp.config(show="*")
    mdp.pack(
        padx=40,
        pady=(5, 15),
        ipady=5
    )
 
    tk.Label(
        fen,
        text="Role",
        bg=BLANC,
        fg=TEXTE,
        font=("Arial", 10, "bold")
    ).pack(anchor="w", padx=40)
 
    role = ttk.Combobox(
        fen,
        values=[
            "Administrateur",
            "Caissier"
        ],
        state="readonly",
        width=27
    )
    role.current(1)
    role.pack(
        padx=40,
        pady=(5, 20),
        ipady=5
    )
 
    def enregistrer():
        if (
            nom.get().strip() == ""
            or mdp.get().strip() == ""
        ):
            messagebox.showwarning(
                "Utilisateur",
                "Tous les champs sont obligatoires."
            )
            return
 
        try:
            executer("""
                INSERT INTO utilisateurs
                (nom, mot_de_passe, role)
                VALUES (?, ?, ?)
            """, (
                nom.get().strip(),
                mdp.get().strip(),
                role.get()
            ))
 
            fen.destroy()
            actualiser_utilisateurs(tree)
 
        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Utilisateur",
                "Ce nom d'utilisateur existe deja."
            )
 
    bouton(
        fen,
        "ENREGISTRER",
        enregistrer,
        VERT,
        20
    ).pack()
 
 
def supprimer_utilisateur(tree):
    selection = tree.selection()
 
    if not selection:
        messagebox.showwarning(
            "Utilisateur",
            "Selectionnez un utilisateur."
        )
        return
 
    valeurs = tree.item(
        selection[0],
        "values"
    )
 
    identifiant = valeurs[0]
    nom = valeurs[1]
 
    if nom == "admin":
        messagebox.showwarning(
            "Securite",
            "Le compte admin principal ne peut pas etre supprime."
        )
        return
 
    if nom == utilisateur_connecte:
        messagebox.showwarning(
            "Securite",
            "Vous ne pouvez pas supprimer votre propre compte."
        )
        return
 
    if messagebox.askyesno(
        "Confirmation",
        "Supprimer cet utilisateur ?"
    ):
        executer(
            "DELETE FROM utilisateurs WHERE id=?",
            (identifiant,)
        )
 
        actualiser_utilisateurs(tree)
 
 
# ============================================================
# LANCEMENT
# ============================================================
 
fenetre = tk.Tk()
fenetre.title("Supermarche Pro")
fenetre.geometry("1180x720")
fenetre.minsize(1050, 650)
fenetre.configure(bg=FOND)
 
style = ttk.Style()
 
try:
    style.theme_use("clam")
except:
    pass
 
style.configure(
    "Treeview",
    background=BLANC,
    fieldbackground=BLANC,
    foreground=TEXTE,
    rowheight=32,
    font=("Arial", 10)
)
 
style.configure(
    "Treeview.Heading",
    background=BLEU_FONCE,
    foreground=BLANC,
    font=("Arial", 10, "bold"),
    padding=8
)
 
style.map(
    "Treeview",
    background=[
        ("selected", BLEU)
    ],
    foreground=[
        ("selected", BLANC)
    ]
)
 
style.configure(
    "TCombobox",
    fieldbackground=BLANC,
    background=BLANC
)
 
creer_base()
afficher_connexion()
 
fenetre.mainloop()
