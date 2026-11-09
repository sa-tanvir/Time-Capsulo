func gen(buf *bytes.Buffer, cmd *Command) {
	for _, c := range cmd.Commands() {
		if !c.IsAvailableCommand() || c == cmd.helpCommand {
			continue
		}
		gen(buf, c)
	}
	commandName := cmd.CommandPath()
	commandName = strings.Replace(commandName, " ", "_", -1)
	commandName = strings.Replace(commandName, ":", "__", -1)

	if cmd.Root() == cmd {
		buf.WriteString(fmt.Sprintf("_%s_root_command()\n{\n", commandName))
	} else {
		buf.WriteString(fmt.Sprintf("_%s()\n{\n", commandName))
	}

	buf.WriteString(fmt.Sprintf("    last_command=%q\n", commandName))
	buf.WriteString("\n")
	buf.WriteString("    command_aliases=()\n")
	buf.WriteString("\n")

	writeCommands(buf, cmd)
	writeFlags(buf, cmd)
	writeRequiredFlag(buf, cmd)
	writeRequiredNouns(buf, cmd)
	writeArgAliases(buf, cmd)
	buf.WriteString("}\n\n")
}
