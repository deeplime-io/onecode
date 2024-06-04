## FAQ
> Why did you take Streamlit out of OneCode?

As Streamlit evolves rapidly, it is difficult to maintain and always run behind API changes.
Especially for community packages that we relied on and are barely or no longer maintained.
Streamlit is a great tool, period. However for our use case, it started to become difficult to
make OneCode evolve and keep Streamlit along, especially as our cloud platform has its own way
of working. You can actually still use Streamlit in Onecode: checkout the `onecode-streamlit`
project.

> Why do I need OneCode at all, I could just build my application with Streamlit?

That's absolutely true, Streamlit or other alternatives are perfectly suitable for that.
However beware of the limitations you can hit (file size handling, data caching, server overload, etc.).
There are scenarios that can work out without OneCode and that's definitely ok: pick the right tool for your use case.
When it comes to deploying your application for different purposes (batch, interactive, long process, large file processing, etc.)
or in different environments, you may find handy to not have to adapt your original code: it will
definitely save you time and frustration and let you focus on the gist of the work rather than the
deployment work.
