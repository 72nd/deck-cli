# deck-cli

 <p align="center">
  <img width="140" src="misc/header.png">
</p>

deck-cli is a command-line tool for interacting with Nextcloud's [Deck Plugin](https://apps.nextcloud.com/apps/deck) by using it's [API](https://deck.readthedocs.io/en/latest/API/). I developed this tool to speed up working with Deck. Thus this application only covers a part of Deck's capabilities.


## Installation

```shell script
git clone https://github.com/72nd/deck-cli.git
cd deck-cli
pip install .
```


## Configuration

To connect with your Nextcloud instance deck-cli needs some informations. For this a configuration YAML file is used. A generic default config file can be created by using the `config` command:

```shell script
deck-cli config path/to/config.yaml
```

Now open the file in your editor and adapt it to your installation.

```yaml
# URL of your Nextcloud instance.
url: nc.example.com

# Nextcloud username
user: usr

# Password for the Nexcloud user
password: secret

# Defines stacks which contain the backlog (tasks not started yet).
# Used for the report generation.
backlog_stacks:
- Backlog

# Defines stacks which contain tasks in active processing. Used for
# the report generation.
progress_stacks:
- In Progress

# Defines the Name of stacks which contains done tasks. Used for the
# report generation.
done_stacks:
- Done

# Names of Boards which should be ignored.
ignore_board:
- Personal

# Define the timezone you'll enter dates into the application. This
# will most probably be your local timezone.
timezone: Europe/Berlin
```


## Add Card

You can use deck-cli to interactively add new Cards to your Nextcloud using the `deck-cli add path/to/config.yaml` command. The names of Boards, Stacks etc. will be fetched from the API and be used for validation prior to submitting the data. Further auto-completion is used whenever possible. 

![Add Screenshot](misc/add.png)


## Report

On Nextcloud the Deck application doesn't allow you to get an Overview over all Cards you have access to. deck-cli can generate an overview report as a markdown file.

```shell script
deck-cli report config.yaml -o report.md
```

The report then can be saved to Nextcloud where it can be viewed (see the complete example report [here](misc/example-report.md)).

![Report in Nextcloud](misc/report-nextcloud.png)
