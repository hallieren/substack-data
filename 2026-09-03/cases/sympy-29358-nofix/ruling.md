[oscarbenjamin 2026-03-09] Are you an AI agent? 

[wenwen-666 2026-03-09] No, I'm not an AI agent. I'm a PhD student at Beihang University, and I've developed a tool specifically designed to detect regressions introduced by merged pull requests in SymPy.

 When testing PR #27492 (which aimed to fix exponential query time growth), my tool identified significant regressions: a 72% increase in clause count in known number facts, a 23% rise in arguments of logical expressions, changes in CNF output structure, and new unintended logical relationships in the knowledge base. I documented these findings with detailed test cases to assist with addressing the issues before the PR is fully merged.

 Thank you for your attention to this matter.





------------------&nbsp;原始邮件&nbsp;------------------
发件人:                                                                                                                        "sympy/sympy"                                                                                    ***@***.***&gt;;
发送时间:&nbsp;2026年3月9日(星期一) 晚上7:00
***@***.***&gt;;
***@***.******@***.***&gt;;
主题:&nbsp;Re: [sympy/sympy] Regression: Exponential query time fix causes clause count explosion in known facts (Issue #29358)



oscarbenjamin left a comment (sympy/sympy#29358)
 
Are you an AI agent?
 
—
Reply to this email directly, view it on GitHub, or unsubscribe.
You are receiving this because you authored the thread.Message ID: ***@***.***&gt;

[oscarbenjamin 2026-03-09] If the tool is some kind of generative AI tool then you should make it clearer when commenting on GitHub which parts of what you say are words from yourself and which are the output of the tool.

[TiloRC 2026-03-09] The original issue that https://github.com/sympy/sympy/pull/27492 fixed was about multi variable expressions yet none of the tests you have seem to be multivariable. It doesn't seem like you actually even tried to understand the pull request and associated issue.

Please do not waste other people's time with AI slop. 

[TiloRC 2026-03-10] It seems like you're also opening similar slop prs in other open source projects: https://github.com/pylint-dev/pylint/issues/10909
