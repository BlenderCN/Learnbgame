bundle = osc_bundle_builder.OscBundleBuilder(
    osc_bundle_builder.IMMEDIATELY)
msg = osc_message_builder.OscMessageBuilder(address="/SYNC")
msg.add_arg(4.0)
# Add 4 messages in the bundle, each with more arguments.
bundle.add_content(msg.build())
msg.add_arg(2)
bundle.add_content(msg.build())
msg.add_arg("value")
bundle.add_content(msg.build())
msg.add_arg(b"\x01\x02\x03")
bundle.add_content(msg.build())

sub_bundle = bundle.build()
# Now add the same bundle inside itself.
bundle.add_content(sub_bundle)
# The bundle has 5 elements in total now.

bundle = bundle.build()
# You can now send it via a client as described in other examples.