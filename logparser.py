#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import ply.lex as lex
import ply.yacc as yacc

reserved = {
    'SSHD' : 'SSHD' ,
    'FAILED' : 'FAILED' ,
    'PASSWORD' : 'PASSWORD' ,
    'FOR' : 'FOR' ,
    'FROM' : 'FROM' ,
    'PORT' : 'PORT' ,
    'SSH2' : 'SSH2' ,
    'DROPBEAR' : 'DROPBEAR' ,
    'BAD' : 'BAD' ,
    'ATTEMPT' : 'ATTEMPT' ,
    'AUTH' : 'AUTH' ,
    'SUCCEEDED' : 'SUCCEEDED' ,
    'ACCEPTED' : 'ACCEPTED'
}

tokens = [
    'IP','LBRACKET','RBRACKET','COLON','QUOTE','NUMBER','IDENTIFY', 'EQUALS',
    'LPAREN','RPAREN','SEM','PLUS','MINUS','TIMES','DIVIDE','POINT','GT','LT',
    'AND' ,'COMMA',
] + list (reserved.values() )

t_SSHD = r'sshd'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COLON = r':'
t_QUOTE = r'\''
t_EQUALS  = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_SEM = r';'
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_POINT = r'\.'
t_GT = r'>'
t_LT = r'<'
t_AND = r'\&'
t_COMMA = r','

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
    t.type = reserved.get( t.value.upper() ,'IDENTIFY')
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

def p_expression(p) :
    '''
    expression : ssh
            | dropbear_failed
            | dropbear_success
    '''
    p[0] = p[1]

def p_ssh(p) :
    '''ssh : IDENTIFY SSHD LBRACKET NUMBER RBRACKET COLON ssh_state PASSWORD FOR IDENTIFY FROM IP PORT NUMBER SSH2'''
    ret = {
        'type' : p[7] ,
        'host' : p[1] ,
        'user' : p[10] ,
        'ip' : p[12] ,
        'port' : p[14] ,
    }
    p[0] = ret
    

def p_dropbear_failed(p) :
    'dropbear_failed : DROPBEAR LBRACKET NUMBER RBRACKET COLON BAD PASSWORD ATTEMPT FOR QUOTE IDENTIFY QUOTE FROM IP COLON NUMBER'
    ret = {
        'type' : 'failed' ,
        'host' : 'dropbear' ,
        'user' : p[11] ,
        'ip' : p[14] ,
        'port' : p[16] ,
    }
    p[0] = ret

def p_dropbear_success(p) :
    'dropbear_success : DROPBEAR LBRACKET NUMBER RBRACKET COLON PASSWORD AUTH SUCCEEDED FOR QUOTE IDENTIFY QUOTE FROM IP COLON NUMBER'
    ret = {
        'type' : 'success' ,
        'host' : 'dropbear' ,
        'user' : p[11] ,
        'ip' : p[14] ,
        'port' : p[16] ,
    }
    p[0] = ret

def p_ssh_state(p) :
    ''' ssh_state : ACCEPTED
                | FAILED
    '''
    if p[1].upper() == 'ACCEPTED' :
        p[0] = 'success'
    else :
        p[0] = 'failed'

def p_error(p) :
    return None

lexer = lex.lex()
parser = yacc.yacc()
