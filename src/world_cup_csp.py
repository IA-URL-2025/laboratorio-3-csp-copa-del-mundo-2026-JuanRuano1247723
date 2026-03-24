import copy

class WorldCupCSP:
    def __init__(self, teams, groups, debug=False):
        """
        Inicializa el problema CSP para el sorteo del Mundial.
        :param teams: Diccionario con los equipos, sus confederaciones y bombos.
        :param groups: Lista con los nombres de los grupos (A-L).
        :param debug: Booleano para activar trazas de depuración.
        """
        self.teams  = teams
        self.groups = groups
        self.debug  = debug

        # Las variables son los equipos.
        self.variables = list(teams.keys())

        # El dominio de cada variable inicialmente son todos los grupos.
        self.domains = {team: list(groups) for team in self.variables}

    
    def get_team_confederation(self, team):
        return self.teams[team]["conf"]

    def get_team_pot(self, team):
        return self.teams[team]["pot"]

    def _get_group_teams(self, group, assignment):
        return [t for t, g in assignment.items() if g == group]

    def _count_confederation_in_group(self, conf, group_teams):
        return sum(1 for t in group_teams if self.get_team_confederation(t) == conf)

    def _has_pot_conflict(self, pot, group_teams):
        return any(self.get_team_pot(t) == pot for t in group_teams)

    def is_valid_assignment(self, group, team, assignment):
        """
        Verifica si asignar un equipo a un grupo viola
        las restricciones de confederación o tamaño del grupo.
        """
        # TODO: implementar restricción de tamaño del grupo (máximo 4)
        # TODO: implementar restricción de que no puede haber dos equipos del mismo bombo
        # TODO: implementar restricción de confederaciones (máximo 1, excepto UEFA máximo 2)

        # Este es un valor de retorno por defecto, debes modificarlo
        group_teams = self._get_group_teams(group, assignment)

        # Restricción de tamaño: máximo 4 equipos por grupo
        if len(group_teams) >= 4:
            return False

        # Restricción de bombo: no puede haber dos equipos del mismo bombo
        if self._has_pot_conflict(self.get_team_pot(team), group_teams):
            return False

        # Restricción de confederación
        conf       = self.get_team_confederation(team)
        conf_count = self._count_confederation_in_group(conf, group_teams)

        if conf == "UEFA":
            if conf_count >= 2:   # UEFA: máximo 2 por grupo
                return False
        else:
            if conf_count >= 1:   # Resto: máximo 1 por grupo
                return False

        return True

    def forward_check(self, assignment, domains):
        """
        Propagación de restricciones.
        Debe eliminar valores inconsistentes en dominios futuros.
        Retorna True si la propagación es exitosa, False si algún dominio queda vacío.
        """
        # Hacemos una copia de los dominios actuales para modificarla de forma segura
        new_domains = copy.deepcopy(domains)

        # TODO: implementar forward checking para filtrar grupos inválidos
        # en los dominios de las variables no asignadas.

        # Este es un valor de retorno por defecto, debes modificarlo
        for team in self.variables:
            if team in assignment:
                continue  # ya asignado, se omite

            new_domains[team] = [
                g for g in new_domains[team]
                if self.is_valid_assignment(g, team, assignment)
            ]

            if not new_domains[team]:
                if self.debug:
                    print(f"  [FC] Dominio vacío para {team} → poda")
                return False, new_domains

        return True, new_domains

    def select_unassigned_variable(self, assignment, domains):
        """
        Heurística MRV (Minimum Remaining Values).
        Selecciona la variable no asignada con el dominio más pequeño.
        """
        # TODO: implementar MRV

        # Este es un valor de retorno por defecto, debes modificarlo
        unassigned = [v for v in domains if v not in assignment]
        if not unassigned:
            return None
        return min(unassigned, key=lambda v: len(domains[v]))

    def order_domain_values(self, var, assignment, domains):
        """
        Devuelve los valores del dominio de `var` en el orden actual.
        (Puede extenderse con heurística LCV si se desea.)
        """
        return domains[var]

    def backtrack(self, assignment, domains=None):
        """
        Backtracking search para resolver el CSP.
        """
        """
        BACKTRACK(assignment, csp)  →  implementado como  backtrack(assignment, domains)

        Pseudocódigo de referencia:
            if len(assignment) == len(csp.variables): return assignment
            var = select_unassigned_variable(csp, assignment)
            for team in order_domain_values(var, assignment, csp):
                if is_valid_assignment(var, team, assignment):
                    assignment[var] = team
                    local_consistent = forward_check(csp, var, team, assignment)
                    if local_consistent:
                        result = BACKTRACK(assignment, csp)
                        if result is not None:
                            return result
                    del assignment[var]   # backtrack
            return None

        Nota: variables=equipos, valores=grupos (convención requerida por los tests).
        La lógica de búsqueda es idéntica al pseudocódigo.
        """
        if domains is None:
            domains = copy.deepcopy(self.domains)

        # Condición de parada: Si todas las variables están asignadas, retornamos la asignación.
        if len(assignment) == len(self.variables):
            return assignment

        # TODO: implementar algoritmo de backtracking
        # 1. Seleccionar variable con MRV
        # 2. Iterar sobre sus valores (grupos) posibles en el dominio
        # 3. Verificar si es válido, hacer la asignación y aplicar forward checking
        # 4. Llamada recursiva
        # 5. Deshacer la asignación si falla (backtrack)

        # ── Selección de variable (MRV) ──────────────────────────────────
        # Equivale a:  var = select_unassigned_variable(csp, assignment)
        var = self.select_unassigned_variable(assignment, domains)
        if var is None:
            return None

        # ── Iteración sobre el dominio ordenado ──────────────────────────
        # Equivale a:  for team in order_domain_values(var, assignment, csp)
        for group in self.order_domain_values(var, assignment, domains):

            # Verificar restricciones
            # Equivale a:  if is_valid_assignment(var, team, assignment)
            if self.is_valid_assignment(group, var, assignment):

                assignment[var] = group
                saved_domains = copy.deepcopy(domains)  # snapshot para backtrack

                if self.debug:
                    print(
                        f"Asignando {var} "
                        f"({self.get_team_confederation(var)}, "
                        f"Bombo {self.get_team_pot(var)}) "
                        f"-> Grupo {group}"
                    )

                # Propagación de restricciones hacia el futuro
                # Equivale a:  local_consistent = forward_check(csp, var, team, assignment)
                local_consistent, new_domains = self.forward_check(assignment, domains)

                if local_consistent:
                    # Llamada recursiva
                    result = self.backtrack(assignment, new_domains)
                    if result is not None:
                        return result

                # ── Backtrack: deshacer asignación y restaurar dominios ──
                del assignment[var]
                domains = saved_domains

                if self.debug:
                    print(f"Backtrack: deshaciendo {var} del Grupo {group}")
       
        # Este es un valor de retorno por defecto, debes modificarlo
        return None