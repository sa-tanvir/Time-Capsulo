func GenYamlCustom(cmd *cobra.Command, w io.Writer, linkHandler func(string) string) error {
	cmd.InitDefaultHelpCmd()
	cmd.InitDefaultHelpFlag()

	yamlDoc := cmdDoc{}
	yamlDoc.Name = cmd.CommandPath()

	yamlDoc.Synopsis = forceMultiLine(cmd.Short)
	yamlDoc.Description = forceMultiLine(cmd.Long)

	if len(cmd.Example) > 0 {
		yamlDoc.Example = cmd.Example
	}

	flags := cmd.NonInheritedFlags()
	if flags.HasFlags() {
		yamlDoc.Options = genFlagResult(flags)
	}
	flags = cmd.InheritedFlags()
	if flags.HasFlags() {
		yamlDoc.InheritedOptions = genFlagResult(flags)
	}

	if hasSeeAlso(cmd) {
		result := []string{}
		if cmd.HasParent() {
			parent := cmd.Parent()
			result = append(result, parent.CommandPath()+" - "+parent.Short)
		}
		children := cmd.Commands()
		sort.Sort(byName(children))
		for _, child := range children {
			if !child.IsAvailableCommand() || child.IsAdditionalHelpTopicCommand() {
				continue
			}
			result = append(result, child.Name()+" - "+child.Short)
		}
		yamlDoc.SeeAlso = result
	}

	final, err := yaml.Marshal(&yamlDoc)
	if err != nil {
		fmt.Println(err)
		os.Exit(1)
	}

	if _, err := w.Write(final); err != nil {
		return err
	}
	return nil
}
