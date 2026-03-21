import copy

class WorldCupCSP:
    def __init__(self, teams, groups, debug=False):
        """
        Inicializa el problema CSP para el sorteo del Mundial.
        :param teams: Diccionario con los equipos, sus confederaciones y bombos.
                      Cada equipo debe tener las claves: 'conf', 'pot'.
                      Opcionalmente 'host_group' si es anfitrión.
        :param groups: Lista con los nombres de los grupos (A-L).
        :param debug: Booleano para activar trazas de depuración.
        """
        self.teams = teams
        self.groups = groups
        self.debug = debug

        # Las variables son los equipos.
        self.variables = list(teams.keys())

        # El dominio de cada variable inicialmente son todos los grupos.
        self.domains = {team: list(groups) for team in self.variables}

        # Restringir dominios de los anfitriones a su grupo preasignado
        for team, info in teams.items():
            if 'host_group' in info:
                self.domains[team] = [info['host_group']]

        # Número total de equipos UEFA (para el balance global)
        self.total_uefa = sum(1 for t in teams.values() if t['conf'] == 'UEFA')
        # Número de grupos
        self.num_groups = len(groups)
        # Valores objetivo para el balance UEFA
        self.uefa_per_group_min = self.total_uefa // self.num_groups
        self.uefa_per_group_max = self.uefa_per_group_min + 1
        # Cantidad de grupos que deben tener el máximo
        self.groups_with_max = self.total_uefa % self.num_groups

    def get_team_confederation(self, team):
        return self.teams[team]["conf"]

    def get_team_pot(self, team):
        return self.teams[team]["pot"]

    def is_valid_assignment(self, group, team, assignment):
        """
        Verifica si asignar un equipo a un grupo viola
        las restricciones de confederación o tamaño del grupo.
        """
        # Obtener equipos ya asignados al grupo
        current = [t for t, g in assignment.items() if g == group]
        # 1. Tamaño del grupo (máximo 2)
        if len(current) >= 2:
            return False
        # 2. Un equipo por bombo por grupo
        team_pot = self.get_team_pot(team)
        for t in current:
            if self.get_team_pot(t) == team_pot:
                return False
        # 3. Restricciones de confederación
        # Contar equipos por confederación en el grupo (incluyendo el nuevo)
        conf_counts = {}
        for t in current:
            c = self.get_team_confederation(t)
            conf_counts[c] = conf_counts.get(c, 0) + 1
        c_team = self.get_team_confederation(team)
        conf_counts[c_team] = conf_counts.get(c_team, 0) + 1
        for conf, count in conf_counts.items():
            if conf == "UEFA":
                if count > 2:
                    return False
            else:
                if count > 1:
                    return False
        # 4. Anfitrión preasignado
        team_info = self.teams[team]
        if 'host_group' in team_info:
            if team_info['host_group'] != group:
                return False
        return True

    def uefa_balance_feasible(self, assignment):
        """
        Verifica si el balance global de UEFA es alcanzable con la asignación actual.
        Se asume que todos los equipos restantes pueden ser colocados de alguna manera.
        Retorna True si es factible, False en caso contrario.
        """
        # Contar UEFA actual por grupo
        uefa_per_group = {}
        for t, g in assignment.items():
            if self.get_team_confederation(t) == "UEFA":
                uefa_per_group[g] = uefa_per_group.get(g, 0) + 1
        # Equipos UEFA restantes
        assigned_uefa = sum(uefa_per_group.values())
        remaining_uefa = self.total_uefa - assigned_uefa

        # Si ya no quedan UEFA, verificar que ningún grupo exceda el máximo permitido
        if remaining_uefa == 0:
            for count in uefa_per_group.values():
                if count > self.uefa_per_group_max:
                    return False
            return True

        # Para cada grupo, calcular cuántos equipos más puede recibir (total y UEFA)
        # y los requisitos mínimos de UEFA para alcanzar el objetivo
        # Primero, contar equipos totales por grupo
        total_per_group = {}
        for t, g in assignment.items():
            total_per_group[g] = total_per_group.get(g, 0) + 1
        # Los grupos que aún tienen cupo (máximo 2)
        remaining_slots = {}
        for g in self.groups:
            used = total_per_group.get(g, 0)
            remaining_slots[g] = 2 - used  # cada grupo tiene 2 slots

        # Calcular mínimo y máximo de UEFA que puede terminar en cada grupo
        # Mínimo: si podemos evitar poner más UEFA, lo hacemos, pero a veces es forzado
        # Para simplificar, usamos una cota: cada grupo puede recibir como máximo
        # el mínimo entre sus slots restantes y (max_uefa - uefa_actual)
        # y como mínimo, debe recibir al menos (min_uefa - uefa_actual) si es positivo,
        # pero si los slots restantes no alcanzan, es imposible.
        min_uefa_needed = 0
        max_uefa_possible = 0
        for g in self.groups:
            current_uefa = uefa_per_group.get(g, 0)
            # Si ya excede el máximo, inviable
            if current_uefa > self.uefa_per_group_max:
                return False
            # Slots restantes
            slots = remaining_slots[g]
            # Máximo UEFA adicional que podemos poner en este grupo
            max_add = min(slots, self.uefa_per_group_max - current_uefa)
            max_uefa_possible += max_add
            # Mínimo UEFA adicional que necesitamos poner para llegar al mínimo objetivo
            min_needed = max(0, self.uefa_per_group_min - current_uefa)
            # Si los slots restantes son menores que lo necesario, inviable
            if min_needed > slots:
                return False
            min_uefa_needed += min_needed

        # Verificar si podemos cumplir con los restantes
        if remaining_uefa < min_uefa_needed or remaining_uefa > max_uefa_possible:
            return False
        return True

    def forward_check(self, assignment, domains):
        """
        Propagación de restricciones.
        Elimina valores inconsistentes en dominios futuros.
        Retorna (True, nuevos_dominios) si la propagación es exitosa,
        (False, None) si algún dominio queda vacío.
        """
        new_domains = copy.deepcopy(domains)
        # Para cada variable no asignada, filtrar su dominio
        for var in self.variables:
            if var in assignment:
                continue
            # Lista de grupos que siguen siendo válidos
            valid_groups = []
            for grp in new_domains[var]:
                # Simular asignación temporal y verificar validez
                if self.is_valid_assignment(grp, var, assignment):
                    valid_groups.append(grp)
            if not valid_groups:
                return False, None
            new_domains[var] = valid_groups
        return True, new_domains

    def select_unassigned_variable(self, assignment, domains):
        """
        Heurística MRV (Minimum Remaining Values).
        Selecciona la variable no asignada con el dominio más pequeño.
        """
        unassigned = [v for v in self.variables if v not in assignment]
        if not unassigned:
            return None
        # Elegir la variable con el dominio de menor tamaño
        best_var = min(unassigned, key=lambda v: len(domains[v]))
        return best_var

    def backtrack(self, assignment, domains=None):
        """
        Backtracking search para resolver el CSP.
        """
        if domains is None:
            domains = copy.deepcopy(self.domains)

        # Condición de parada: todas las variables asignadas
        if len(assignment) == len(self.variables):
            # Verificar balance UEFA al final (global)
            if self.uefa_balance_feasible(assignment):
                return assignment
            else:
                return None  # no cumple balance, falla

        # Seleccionar variable con MRV
        var = self.select_unassigned_variable(assignment, domains)
        if var is None:
            return None

        # Ordenar valores (podría implementarse alguna heurística)
        for grp in domains[var]:
            # Verificar si la asignación es válida con el estado actual
            if not self.is_valid_assignment(grp, var, assignment):
                continue

            # Realizar asignación
            new_assignment = assignment.copy()
            new_assignment[var] = grp

            # Forward checking
            success, new_domains = self.forward_check(new_assignment, domains)
            if not success:
                continue

            # Verificar factibilidad del balance UEFA (global)
            if not self.uefa_balance_feasible(new_assignment):
                continue

            # Llamada recursiva
            result = self.backtrack(new_assignment, new_domains)
            if result is not None:
                return result

        return None