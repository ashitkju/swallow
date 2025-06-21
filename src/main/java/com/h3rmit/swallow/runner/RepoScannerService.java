package com.h3rmit.swallow.runner;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.ClassOrInterfaceDeclaration;
import com.github.javaparser.utils.SourceRoot;
import com.h3rmit.swallow.dto.ClassInfo;
import com.h3rmit.swallow.dto.MethodInfo;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

@Component
public class RepoScannerService implements ApplicationRunner {

    @Override
    public void run(ApplicationArguments args) throws IOException {
        System.out.println("Scanning...");
        ClassPathResource classPathResource = new ClassPathResource("static");
        Path repoPath = Paths.get(classPathResource.getFile().getAbsolutePath(), "/java");

        SourceRoot sourceRoot = new SourceRoot(repoPath);
        List<ClassInfo> classInfoList = new ArrayList<>();
        List<ParseResult<CompilationUnit>> units = sourceRoot.tryToParse("");

        for (ParseResult<CompilationUnit> unitResult : units) {
            unitResult.getResult().ifPresent(unit -> {
                unit.getTypes().forEach(type -> {
                    if (type instanceof ClassOrInterfaceDeclaration clazz) {
                        String className = clazz.getNameAsString();
                        String filePath = unit.getStorage().map(s -> s.getPath().toString()).orElse("Unknown");

                        ClassInfo classInfo = new ClassInfo(className, filePath);

                        clazz.getMethods().forEach(method -> {
                            classInfo.methods().add(new MethodInfo(method.getNameAsString()));
                        });

                        unit.getAllContainedComments().forEach(comment -> {
                            classInfo.comments().add(comment.getContent().strip());
                        });

                        classInfoList.add(classInfo);
                    }
                });
            });
        }

        ObjectMapper mapper = new ObjectMapper();
        mapper.writerWithDefaultPrettyPrinter().writeValue(new File("code_metadata.json"), classInfoList);

        System.out.println("✅ Metadata written to code_metadata.json");
    }
}
