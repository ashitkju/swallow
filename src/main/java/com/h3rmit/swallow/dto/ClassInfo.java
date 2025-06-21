package com.h3rmit.swallow.dto;

import java.util.ArrayList;
import java.util.List;

public record ClassInfo(String className, String filePath, List<String> comments, List<MethodInfo> methods) {
    public ClassInfo(String className, String filePath) {
        this(className, filePath, new ArrayList<>(), new ArrayList<>());
    }
}
