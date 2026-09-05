# integrate `exp(x)*sin(x**2 + x)*cos(x)` hangs indefinitely

SymPy cannot solve this type of integrals and instead of returning a `DontKnowRule`, it just keeps trying. The only way to solve this type of integrals is probably to rewrite sins/cos in terms of complex exponentials.

Wolfram Alpha:

<img width="1040" height="345" alt="Image" src="https://github.com/user-attachments/assets/2b9898a9-55b6-4a13-bcc1-003612019ea2" />
