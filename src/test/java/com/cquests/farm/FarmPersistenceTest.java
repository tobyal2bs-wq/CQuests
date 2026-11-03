package com.cquests.farm;

import com.cquests.CQuestsPlugin;
import org.bukkit.configuration.file.YamlConfiguration;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import java.nio.file.*;
import java.nio.file.attribute.FileTime;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.logging.Logger;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class FarmPersistenceTest {
    @TempDir Path folder;
    private FarmService service(){
        var plugin=mock(CQuestsPlugin.class);when(plugin.getName()).thenReturn("CQuests");
        when(plugin.getDataFolder()).thenReturn(folder.toFile());when(plugin.getLogger()).thenReturn(Logger.getAnonymousLogger());
        return new FarmService(plugin);
    }
    @SuppressWarnings("unchecked") private Set<FarmService.Spot> pending(FarmService service)throws Exception {
        var field=FarmService.class.getDeclaredField("pending");field.setAccessible(true);return (Set<FarmService.Spot>)field.get(service);
    }
    private void drain(FarmService service)throws Exception {
        var field=FarmService.class.getDeclaredField("writer");field.setAccessible(true);((ExecutorService)field.get(service)).submit(()->{}).get();
    }
    @Test void unchangedSnapshotsDoNotRewriteButCropChangesAndShutdownPersist()throws Exception {
        var service=service();Path file=folder.resolve("farm-regrowth.yml");
        try{
            service.savePending();drain(service);assertTrue(Files.isRegularFile(file));
            FileTime marker=FileTime.fromMillis(1000000);Files.setLastModifiedTime(file,marker);
            for(int i=0;i<50;i++)service.savePending();drain(service);assertEquals(marker,Files.getLastModifiedTime(file));
            var crop=new FarmService.Spot("world",10,64,20);pending(service).add(crop);service.savePending();drain(service);
            assertEquals(java.util.List.of(crop.encode()),YamlConfiguration.loadConfiguration(file.toFile()).getStringList("pending"));
            pending(service).remove(crop);
        }finally{service.shutdown();}
        assertTrue(YamlConfiguration.loadConfiguration(file.toFile()).getStringList("pending").isEmpty());
    }
    @Test void failedReplacementDoesNotSuppressRetryOfTheSameSnapshot()throws Exception {
        var service=service();Path file=folder.resolve("farm-regrowth.yml");
        try{
            service.savePending();drain(service);Files.delete(file);Files.createDirectory(file);Files.writeString(file.resolve("blocker"),"test");
            var crop=new FarmService.Spot("world",1,64,2);pending(service).add(crop);service.savePending();drain(service);
            assertTrue(Files.isDirectory(file));Files.delete(file.resolve("blocker"));Files.delete(file);
            service.savePending();drain(service);
            assertEquals(java.util.List.of(crop.encode()),YamlConfiguration.loadConfiguration(file.toFile()).getStringList("pending"));
        }finally{service.shutdown();}
    }
}
