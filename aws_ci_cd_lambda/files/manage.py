#!/usr/bin/env python


def runner(event, lambda_context):
    message = 'Hello, world!'

    return { 
        'message': message
    }  
