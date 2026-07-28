# dp — design pattern generator

`dp` gera scaffolding de padrões de projeto em duas etapas. Na primeira
execução ele cria um `key.yaml` editável. Na segunda, lê esse arquivo e gera os
códigos com Jinja2.

## Instalação

Com `pipx`:

```bash
pipx install .
```

Ou em um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

Durante o desenvolvimento:

```bash
python -m pip install -e .
```

## Uso

```bash
dp --list
dp --java singleton
dp --cpp singleton
dp --python singleton
dp --java factory
dp --java observer
```

Na primeira execução, somente `key.yaml` é criado. Edite-o e repita o mesmo
comando para gerar o código. Execuções seguintes sobrescrevem as saídas com os
valores atuais do YAML. `--force` torna essa intenção explícita em scripts:

```bash
dp --java singleton --force
```

## Exemplo completo

Primeira execução:

```console
$ dp --java singleton
Criado: key.yaml
Edite o arquivo e execute o comando novamente.
```

Edite `key.yaml`:

```yaml
pattern: singleton
language: java
package: br.eng.ivanlopes.patterns
class_name: AppSingleton
instance_method: getInstance
output_dir: src/main/java/br/eng/ivanlopes/patterns
thread_safe: true
```

Segunda execução:

```console
$ dp --java singleton
Gerado: src/main/java/br/eng/ivanlopes/patterns/AppSingleton.java
```

Arquivo gerado:

```java
package br.eng.ivanlopes.patterns;

public final class AppSingleton {
    private static volatile AppSingleton instance;

    private AppSingleton() {
    }

    public static AppSingleton getInstance() {
        if (instance == null) {
            synchronized (AppSingleton.class) {
                if (instance == null) {
                    instance = new AppSingleton();
                }
            }
        }
        return instance;
    }
}
```

## Adicionando um padrão

Crie:

```text
patterns/<linguagem>/<padrao>/
├── key.yaml.tmpl
├── meta.yaml
└── templates/
    └── Arquivo.ext.j2
```

O `meta.yaml` declara os campos e as saídas. O registro escaneia essa estrutura
em runtime; não é necessário editar o código Python.

## Testes

```bash
python -m unittest discover -s tests -v
```
