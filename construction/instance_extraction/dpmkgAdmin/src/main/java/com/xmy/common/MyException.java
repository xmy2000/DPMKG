package com.xmy.common;

import lombok.NoArgsConstructor;

@NoArgsConstructor
public class MyException extends Exception {
    public MyException(String msg) {
        super(msg);
    }
}
