package com.cbosses.util;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;

/**
 * Writes a data file so it can never be left half written: the text goes to a temporary file first, the old
 * file is kept as name.bak, and only then is the new one moved into place. A crash or a full disk mid-save
 * leaves the old file (or its backup) intact.
 */
public final class SafeFiles {
    private SafeFiles() { }

    public static synchronized void write(File file, String text) throws IOException {
        Path target = file.toPath();
        Path dir = target.toAbsolutePath().getParent();
        if (dir != null) Files.createDirectories(dir);
        Path tmp = target.resolveSibling(file.getName() + ".tmp");
        Files.writeString(tmp, text, StandardCharsets.UTF_8);
        if (Files.exists(target) && Files.size(target) > 0)
            Files.copy(target, target.resolveSibling(file.getName() + ".bak"), StandardCopyOption.REPLACE_EXISTING);
        try {
            Files.move(tmp, target, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
        } catch (AtomicMoveNotSupportedException e) {
            Files.move(tmp, target, StandardCopyOption.REPLACE_EXISTING);
        }
    }
}
