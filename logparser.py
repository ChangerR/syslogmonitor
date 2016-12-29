#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import ply.lex as lex

logfail = 'proxy sshd[27827]: Failed password for root from 218.65.30.122 port 52785 ssh2'

reserved = {
    'sshd' : 'SSHD' ,
    'Failed' : 'FAILED' ,
    'password' : 'PASSWORD' ,
    'for' : 'FOR' ,
    'from' : 'FROM' ,
    'port' : 'PORT' ,
    'ssh2' : 'SSH2' ,
}

tokens = [
    'IP','LBRACKET','RBRACKET','COLON','NUMBER','IDENTIFY'
] + list (reserved.values() )

t_SSHD = r'sshd'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COLON = r':'

def t_IP(t) :
    r'\d+\.\d+\.\d+\.\d+'
    return t

# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

def t_IDENTIFY(t) :
    r'\w+'
    t.type = reserved.get(t.value,'IDENTIFY')
    return t
     
# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

lexer.input(logfail)
# Tokenize
while True:
    tok = lexer.token()
    if not tok: 
        break      # No more input
    print(tok)