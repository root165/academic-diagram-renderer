# Notation and design evidence

This file records the normative basis for the skill's ER rules. It separates **standards** from **de facto conventions** and from **house style**, so the model does not claim more authority than a source supports.

## Evidence map

| Claim used by the skill | Source | Status | Consequence for the figure |
| --- | --- | --- | --- |
| A conceptual data model can be expressed with entity sets, attributes, and relationship sets. | P. P.-S. Chen, “The Entity-Relationship Model—Toward a Unified View of Data,” *ACM Transactions on Database Systems* 1(1), 1976, pp. 9–36. [DOI](https://doi.org/10.1145/320434.320440) | Peer-reviewed original definition | Chen notation is legitimate for conceptual analysis: rectangles, ellipses, diamonds. |
| Database design separates conceptual, logical, and physical levels. | R. Elmasri and S. B. Navathe, *Fundamentals of Database Systems*, 7th ed., Pearson, 2016, chs. 3 and 9; D. Tsichritzis and A. Klug, “The ANSI/X3/SPARC DBMS Framework Report,” *Information Systems* 3(3), 1978. | Standard textbook and architecture report | Do not put physical keys, types, or indexes into a conceptual figure; do not leave M:N unresolved in a logical figure. |
| A conceptual M:N relationship is mapped to a relation/associative table with two 1:N links in logical design. | Elmasri and Navathe, *Fundamentals of Database Systems*, 7th ed., ch. 9 (ER/EER-to-relational mapping). | Standard textbook procedure | `维修工单—备件` M:N becomes `wo_spare_record`; relationship attributes become columns there. |
| A foreign key must reference an existing candidate/primary key. | Elmasri and Navathe, chs. 3–5 (relational model and integrity constraints); any SQL-92/MySQL 8.0 reference for the physical implementation. | Relational-model definition | A logical `FK` without a target key is a validation error, not a stylistic choice. |
| Crow's Foot is a de facto Information Engineering convention, not a single ISO standard. | J. Martin, *Information Engineering* (1989–1990); C. Finkelstein, *An Introduction to Information Engineering* (1989). | De facto convention | State the endpoint legend and optionality explicitly; never assume every reader interprets the same crow's foot. |
| Colour must not be the only means of conveying information. | W3C, *Web Content Accessibility Guidelines (WCAG) 2.2*, SC 1.4.1 “Use of Color,” W3C Recommendation, 5 October 2023. [URL](https://www.w3.org/TR/WCAG22/#use-of-color) | Normative accessibility recommendation | Monochrome default; if colour is used, add a non-colour cue and preserve grayscale legibility. |
| Chinese software documents use numbered figures/tables and prescribed section structures. | GB/T 8567—2006, *计算机软件文档编制规范*; GB/T 9385—2008, *计算机软件需求规格说明规范*. | National standards (documentation) | Keep captions numbered and placed consistently; do not invent a section structure that conflicts with the template. |
| Flowchart symbols are standardized separately from ER notation. | ISO 5807:1985, *Information processing — Documentation symbols and conventions for data, program and system flowcharts*. | International standard | Never use flowchart decision diamonds as ER relationship diamonds. |

## What is *not* claimed

- **Crow's Foot is not an ISO standard.** The skill uses it because it is widely understood in database teaching and practice, but the figure must still carry a legend or caption that defines `0..1`, `1..1`, `0..N`, and `1..N`.
- **“Three-line table” is not a national standard.** It is a restrained academic house style. A school or journal template overrides it.
- **“Chen notation” does not require a particular drawing tool.** Graphviz, PlantUML, or a vector editor can implement it; the semantic constructs matter, not the renderer.
- **A conceptual model is not a preview of the DDL.** If the conceptual figure contains `_id` columns, data types, or join tables, it has collapsed two design levels into one and can no longer prove that the business was understood.

## How the evidence is applied

1. **Section first.** Read [section-contract.md](section-contract.md). Decide whether the section asks for a conceptual or logical model before choosing a notation.
2. **Model second.** A conceptual figure may show M:N and relationship attributes. A logical figure must resolve M:N and show PK/FK.
3. **Validate third.** Run `validate_ir.py`; the bundled checks encode the level/notation constraints and the no-FK-in-conceptual rule.
4. **Style last.** Apply [visual-style.md](visual-style.md). The monochrome declaration is part of the IR, not an afterthought applied to the rendered image.
5. **Trace the pair.** When both figures exist, use the pair-consistency table in [section-contract.md](section-contract.md) and keep the same business vocabulary across both.

## Reference list

1. Chen, P. P.-S. (1976). The Entity-Relationship Model—Toward a Unified View of Data. *ACM Transactions on Database Systems*, 1(1), 9–36. https://doi.org/10.1145/320434.320440
2. Elmasri, R., & Navathe, S. B. (2016). *Fundamentals of Database Systems* (7th ed.). Pearson. ISBN 978-0-13-397077-7.
3. Tsichritzis, D., & Klug, A. (1978). The ANSI/X3/SPARC DBMS Framework Report of the Study Group on Data Base Management Systems. *Information Systems*, 3(3), 173–191.
4. Martin, J. (1989–1990). *Information Engineering*. Prentice Hall.
5. Finkelstein, C. (1989). *An Introduction to Information Engineering: From Strategic Planning to Information Systems*. Addison-Wesley.
6. W3C. (2023). *Web Content Accessibility Guidelines (WCAG) 2.2*. https://www.w3.org/TR/WCAG22/
7. GB/T 8567—2006, *计算机软件文档编制规范*.
8. GB/T 9385—2008, *计算机软件需求规格说明规范*.
9. ISO 5807:1985, *Information processing — Documentation symbols and conventions for data, program and system flowcharts*.
