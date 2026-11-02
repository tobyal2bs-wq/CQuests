package com.cquests.data;

/** Plain text only. An entry can never execute a reward, command or component action. */
public record MailEntry(String source,String sender,String text,long time,boolean fromPlayer) {
    public MailEntry {
        if(source==null||!source.matches("[a-z0-9_-]{1,80}")||sender==null||text==null||time<=0)throw new IllegalArgumentException("Invalid mail entry");
        sender=sender.substring(0,Math.min(80,sender.length()));text=text.substring(0,Math.min(1800,text.length()));
    }
}
