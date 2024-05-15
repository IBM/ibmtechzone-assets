prompt=f"""
<<SYS>>
you are an expert in knowledge graph creation, your job is to help extract the ontology for a knowledge graph from text provided by following the steps given below
<</SYS>>
[INST]
- first take a look at the text provided below within <text> </text> tags  about {domain} understand the domain. Then think about what  classes can be extracted from the text in order to make an ontology for a knowledge graph
- once you identify all the classes, define the attributes and properties for each of the classes.try to use the same words as mentioned in the text while defining the attributes and properties.
-  using these properties and attributes, figure out how the classes are related.
- make sure you capture all the relationships between all the classes
- think step by step
- give the output as an ontology schema in JSON format within <JSON> </JSON> tags as shown in the examples below.
- learn from the example given below:
The example below is about a sports domain:
<example>
text:

Cristiano Ronaldo dos Santos Aveiro GOIH ComM (Portuguese pronunciation: [kɾiʃtjɐnu ʁɔnaldu]; born 5 February 1985) is a Portuguese professional footballer who plays as a forward for and captains both Saudi Pro League club Al Nassr and the Portugal national team. Widely regarded as one of the greatest players of all time, Ronaldo has won five Ballon d'Or awards,[note 3] a record three UEFA Men's Player of the Year Awards, and four European Golden Shoes, the most by a European player. He has won 33 trophies in his career, including seven league titles, five UEFA Champions Leagues, the UEFA European Championship and the UEFA Nations League. Ronaldo holds the records for most appearances (183), goals (140) and assists (42) in the Champions League, goals in the European Championship (14), international goals (128) and international appearances (205). He is one of the few players to have made over 1,200 professional career appearances, the most by an outfield player, and has scored over 850 official senior career goals for club and country, making him the top goalscorer of all time.
Ronaldo began his senior career with Sporting CP, before signing with Manchester United in 2003, winning the FA Cup in his first season. He would also go on to win three consecutive Premier League titles, the Champions League and the FIFA Club World Cup; at age 23, he won his first Ballon d'Or. Ronaldo was the subject of the then-most expensive association football transfer when he signed for Real Madrid in 2009 in a transfer worth €94 million (£80 million). He became a key contributor and formed an attacking trio with Karim Benzema and Gareth Bale which was integral to the team winning four Champions Leagues from 2014 to 2018, including La Décima. During this period, he won back-to-back Ballons d'Or in 2013 and 2014, and again in 2016 and 2017, and was runner-up three times behind Lionel Messi, his perceived career rival. He also became the club's all-time top goalscorer and the all-time top scorer in the Champions League, and finished as the competition's top scorer for six consecutive seasons between 2012 and 2018. With Real, Ronaldo won four Champions Leagues, two La Liga titles, two Copas del Rey, two UEFA Super Cups and three Club World Cups. In 2018, he signed for Juventus in a transfer worth an initial €100 million (£88 million), the most expensive transfer for an Italian club and for a player over 30 years old. He won two Serie A titles, two Supercoppa Italiana trophies and a Coppa Italia, became the inaugural Serie A Most Valuable Player and became the first footballer to finish as top scorer in the English, Spanish and Italian leagues. He returned to Manchester United in 2021, finishing his only full season as the club's top scorer, before his contract was terminated in 2022. In 2023, he signed for Al Nassr.
Ronaldo made his international debut for Portugal in 2003 at the age of 18 and has since earned more than 200 caps, making him both the country and history's most-capped player of all time, recognised by the Guinness World Records.[9] With more than 100 goals at international level, he is also the sports all-time top goalscorer. Ronaldo has played in and scored at eleven major tournaments; he scored his first international goal at Euro 2004, where he helped Portugal reach the final. He assumed captaincy of the national team in July 2008. In 2015, Ronaldo was named the best Portuguese player of all time by the Portuguese Football Federation. The following year, he led Portugal to their first major tournament title at Euro 2016, and received the Silver Boot as the second-highest goalscorer of the tournament. This achievement would see him receive his fourth Ballon d'Or. He also led them to victory in the inaugural UEFA Nations League in 2019, receiving the top scorer award in the finals, and later received the Golden Boot as top scorer of Euro 2020.
One of the world's most marketable and famous athletes, Ronaldo was ranked the world's highest-paid athlete by Forbes in 2016, 2017, and 2023, and the world's most famous athlete by ESPN from 2016 to 2019. Time included him on their list of the 100 most influential people in the world in 2014. He is the first footballer and the third sportsman to earn US$1 billion in his career.

Output:

Classes Identified:
- Person (Cristiano Ronaldo)
- Club
- National Team
- Trophy/Award
- Transfer
- Championship
- Record

Attributes and Properties for Each Class:
- Person
Name
Nationality
Date of Birth
Positions (e.g., forward)
Professional Appearances
Senior Career Goals
- Club
Name
League
Country
- National Team
Country
Caps
Goals
Major Tournament Titles
- Trophy/Award
Name
Category (e.g., Individual, Team)
Times Won
Year(s)
- Transfer
From Club
To Club
Transfer Fee
Year
- Championship
Name
Type (e.g., League, Cup, International)
Wins
- Record
Type (e.g., Appearances, Goals, Assists)
Number
Competition

Relationships Between Classes:

Person has relationships with Club (plays for, has transferred to), National Team (represents, captains), Trophy/Award (has won), and Record (holds).
Club is related to Championship (participates in, wins) and Transfer (is part of).
National Team is related to Championship (participates in, wins) and Person (is captained by, includes players).
Trophy/Award is related to both Person and Club (awarded to).
Transfer involves two Clubs and a Person (is transferred from, is transferred to).
Championship involves Clubs and National Teams (winners, participants).

<JSON>
{{
  "classes": {{
    "Person": {{
      "attributes": ["Name", "Nationality", "Date of Birth", "Position", "Professional Appearances", "Senior Career Goals"]
    }},
    "Club": {{
      "attributes": ["Name", "League", "Country"]
    }},
    "National Team": {{
      "attributes": ["Country", "Caps", "Goals", "Major Tournament Titles"]
    }},
    "Award": {{
      "attributes": ["Name", "Category", "Times Won", "Years"]
    }},
    "Championship": {{
      "attributes": ["Name", "Type", "Wins"]
    }},
    "Record": {{
      "attributes": ["Type", "Number", "Competition"]
    }}
  }},
  "relationships": {{
    "Person": {{
      "playsFor": ["Club", "National Team"],
      "hasWon": ["Award", "Championship"],
      "holds": "Record"
    }},
    "Club": {{
      "participatesIn": "Championship",
      "hasPlayer": "Person"
    }},
    "National Team": {{
      "hasPlayer": "Person",
      "participatesIn": "Championship"
    }},
    "Award": {{
      "awardedTo": "Person"
    }},
    "Championship": {{
      "wonBy": ["Club", "National Team"],
      "includesPlayer": "Person"
    }},
    "Record": {{
      "heldBy": "Person"
    }}
  }}
}}
</JSON>

<example>
text:
<text>
{text}
</text>
Output:"""