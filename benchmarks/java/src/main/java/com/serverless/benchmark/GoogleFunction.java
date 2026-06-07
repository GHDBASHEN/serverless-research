package com.serverless.benchmark;

import com.google.cloud.functions.HttpFunction;
import com.google.cloud.functions.HttpRequest;
import com.google.cloud.functions.HttpResponse;
import com.google.gson.Gson;
import java.io.BufferedWriter;
import java.io.IOException;

public class GoogleFunction implements HttpFunction {
    private static final Gson gson = new Gson();
    private final Function function = new Function();

    @Override
    public void service(HttpRequest request, HttpResponse response) throws IOException {
        // Read request body
        Function.Request req;
        try {
            req = gson.fromJson(request.getReader(), Function.Request.class);
        } catch (Exception e) {
            req = new Function.Request();
        }
        if (req == null) {
            req = new Function.Request();
        }

        // Call the core handler
        Function.Response res = function.handleRequest(req);

        // Write response
        response.setContentType("application/json");
        BufferedWriter writer = response.getWriter();
        writer.write(gson.toJson(res));
    }
}
