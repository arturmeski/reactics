package pl.umk.mat.martinp.reactics;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;


public class ReacticsRuntime {
    private static ReacticsRuntime instance = null;

    private String rctPath = "./";
    private String rctRuntime = "reactics";
    private Path rsslFile;

    public static synchronized ReacticsRuntime getInstance() throws ReacticsRuntimeException {
        if (instance == null)
            instance = new ReacticsRuntime();

        return instance;
    }

    private ReacticsRuntime() throws ReacticsRuntimeException {
        try {
            rsslFile = Files.createTempFile("reaction_system_", ".rs");
            rsslFile.toFile().deleteOnExit();
            System.out.println("[ReactICS] Created temporary file: " + rsslFile.toAbsolutePath());
        }
        catch (IOException e) {
            System.err.println("[ReactICS] Problem creating temporary file:  + e.getMessage()");
            throw new ReacticsRuntimeException("Problem creating temporary file:\n" + e.getMessage());
        }
    }

    public Path getRSSLFile() {
        return rsslFile;
    }

    public void loadConfig(String configFileName) throws ConfigReadingError, InvalidRuntimeException {
        System.out.println("[ReactICS] Loading configuration from: " + configFileName);

        try {
            BufferedReader inputStream = new BufferedReader(new FileReader(configFileName));
            String line;

            while ((line = inputStream.readLine()) != null) {
                if (line.startsWith("runtime")) {
                    line = line.replaceAll("\\s", "");
                    rctRuntime = line.substring(line.indexOf(":") + 1);
                }
                else if (line.startsWith("path")) {
                    line = line.replaceAll("\\s", "");
                    rctPath = line.substring(line.indexOf(":") + 1);
                }
            }
        }
        catch (IOException e) {
            throw new ConfigReadingError(e.getMessage());
        }

        File rctRntFile = new File(rctPath + rctRuntime);

        if (! (rctRntFile.exists() && rctRntFile.canExecute()) ) {
            throw new InvalidRuntimeException(rctPath + rctRuntime + " cannot be executed");
        }

        System.out.println("[ReactICS] Using runtime: " + rctPath + rctRuntime);
    }

    public EvalResult evaluateFormula(String fLabel) throws IOException, ReacticsRuntimeException {
        // Drop "-B" option if verification time should not be measured
        Process proc = Runtime.getRuntime().exec(rctPath + rctRuntime + " -B -c " + fLabel + " " + rsslFile.toAbsolutePath(),
                null, new File(rctPath));

        BufferedReader formResultStream = new BufferedReader(new InputStreamReader(proc.getInputStream()));
        String line;
        Formula.FormulaStatus result = Formula.FormulaStatus.None;
        String mcTime = "";
        String totalTime = "";
        String memory = "";

        while ((line = formResultStream.readLine()) != null) {
            if (line.contains("holds")) {
                result = Formula.FormulaStatus.True;
            }
            else if (line.contains("not hold")) {
                result = Formula.FormulaStatus.False;
            }
            else if (line.startsWith("STAT")) {
                String[] tokens = line.split(";");
                mcTime = tokens[2];
                totalTime = tokens[5];
                memory = tokens[4];
            }

            //TODO: Handle incorrect formulas
        }

        StringBuilder errMsg = new StringBuilder();
        BufferedReader procErrStr = new BufferedReader(new InputStreamReader(proc.getErrorStream()));
        while ((line = procErrStr.readLine()) != null) {
            errMsg.append(line).append("\n");
        }

        if (!errMsg.isEmpty())
            throw new ReacticsRuntimeException(errMsg.toString());

        return new EvalResult(result, mcTime, totalTime, memory);
    }

    /** Complete Transition System. Context automaton state included. */
    public String getTransitionSystemStructure() throws IOException, ReacticsRuntimeException {
        Process proc = Runtime.getRuntime().exec(rctPath + rctRuntime + " -t -X " + rsslFile.toAbsolutePath(),
                    null, new File(rctPath));

        String line;
        StringBuilder tsString = new StringBuilder();
        BufferedReader procOutStr = new BufferedReader(new InputStreamReader(proc.getInputStream()));
        while ((line = procOutStr.readLine()) != null) {
            tsString.append(line).append("\n");
        }

        StringBuilder errMsg = new StringBuilder();
        BufferedReader procErrStr = new BufferedReader(new InputStreamReader(proc.getErrorStream()));
        while ((line = procErrStr.readLine()) != null) {
            errMsg.append(line).append("\n");
        }

        if (!errMsg.isEmpty())
            throw new ReacticsRuntimeException(errMsg.toString());

        return tsString.toString();
    }

    public void exportToISPLFile(File outFile) throws IOException, ReacticsRuntimeException {
        Process proc = Runtime.getRuntime().exec(rctPath + rctRuntime + " -e " + rsslFile.toAbsolutePath() + " > " + outFile.getAbsolutePath(),
                    null, new File(rctPath));

        String line;
        BufferedReader procOutStr = new BufferedReader(new InputStreamReader(proc.getInputStream()));
        PrintWriter isplOutStr = new PrintWriter(new FileWriter(outFile));
        while ((line = procOutStr.readLine()) != null) {
            isplOutStr.println(line);
        }
        isplOutStr.close();

        StringBuilder errMsg = new StringBuilder();
        BufferedReader procErrStr = new BufferedReader(new InputStreamReader(proc.getErrorStream()));
        while ((line = procErrStr.readLine()) != null) {
            errMsg.append(line).append("\n");
        }

        if (!errMsg.isEmpty())
            throw new ReacticsRuntimeException(errMsg.toString());
    }

    record EvalResult(Formula.FormulaStatus result, String mcTime, String totalTime, String memory) {}
}

class ConfigReadingError extends Exception {
    public ConfigReadingError(String message) {
        super(message);
    }
}

class InvalidRuntimeException extends Exception {
    public InvalidRuntimeException(String description) {
        super(description);
    }
}

class ReacticsRuntimeException extends Exception {
    public ReacticsRuntimeException(String description) {
        super(description);
    }
}