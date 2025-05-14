# Decent Console
My attempt at improving the ingame console by adding:

- ctrl+backspace to delete the last word
- ctrl+delete to delete the next word
- ctrl+left/right to move the cursor by word
- auto-completion for commands by pressing tab
- switch between suggestions with ctrl+up/down

### Dev notes
If you want your commands to be registered, simply use the sdks ``@command`` decorator. Thats it!  
If your command needs either ``UObject``, ``UClass`` or a ``UProperty`` (of a given object) as an argument, you can use ``$PathName``, ``$ClassName`` or ``$PropertyName`` as ``choice``.
