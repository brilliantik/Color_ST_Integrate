import numpy as np


class RPData:
	Kmu: float = 0.0
	__IsTable: bool = True
	__n1: float = None
	__n2: float = None
	__k1: float = None
	__k2: float = None
	__swmin: float = 0.0
	__swmax: float = 1.0
	__table = None
	__TABLE_DS: float = 0.001
	__TABLE_NODES: int = 1000 + 1

	def Ready(self) -> bool:
		if self.Kmu <= 0.0:
			return False
		if self.__IsTable:
			return self.__table is not None and self.__table.__len__() > 1
		else:
			return self.__k1 > 0 and self.__k2 > 0 and self.__n1 >= 0 and self.__n2 >= 0

	def ToString(self) -> str:
		return "Ready={0}, Kmu={1}, Tbl={2}".format(self.Ready(), self.Kmu, self.__IsTable)

	def __init__(self, fn: str):
		try:
			sr = open(fn, 'r')
			try:
				buf = sr.readline().split()
				self.Kmu = float(buf[0])
				buf = sr.readline().split()
				m: int = int(buf[0])
				if m == 0:
					self.__IsTable = True
					buf = sr.readline().split()
					n: int = int(buf[0])
					fileTable = []
					for i in range(n):
						buf = sr.readline().split()
						t = (float(buf[0]), float(buf[1]), float(buf[2]))
						fileTable.append(t)
					self.__FormTable(fileTable)
				else:
					self.__IsTable = False
					self.__k1 = float(buf[1])
					self.__k2 = float(buf[2])
					self.__n1 = float(buf[3])
					self.__n2 = float(buf[4])
					if buf.__len__() >= 7:
						self.__swmin = float(buf[5])
						self.__swmax = float(buf[6])
			finally:
				sr.close()
		except:
			print('Error constructor RPData class!')

	def __FormTable(self, filetable):
		self.__table = None
		if filetable is None:
			return
		n: int = filetable.__len__()
		if n < 2:
			return
		self.__table = []
		s0: float
		s1: float
		s: float
		m: float
		k10: float
		k20: float
		k11: float
		k21: float
		self.__k1 = 0.0
		self.__k2 = 0.0
		i0: int = 0
		for i in range(self.__TABLE_NODES):
			s = i * self.__TABLE_DS
			s0 = filetable[0][0]
			k10 = filetable[0][1]
			k20 = filetable[0][1]
			if s < s0:
				self.__k1 = 0.0
				self.__k2 = 1.0 - s * (1.0 - k20) / s0
			else:
				found: bool = False
				for f in range(i0 + 1, n):
					s1 = filetable[f][0]
					k11 = filetable[f][1]
					k21 = filetable[f][2]
					if s <= s1:
						s0 = filetable[f - 1][0]
						k10 = filetable[f - 1][1]
						k20 = filetable[f - 1][2]
						m = (s - s0) / (s1 - s0)
						self.__k1 = k10 + m * (k11 - k10)
						self.__k2 = k20 + m * (k21 - k20)
						found = True
						i0 = f - 1
						break
				if not found:
					s1 = filetable[n - 1][0]
					k11 = filetable[n - 1][1]
					self.__k1 = k11 + (s - s1) * (1.0 - k11) / (1.0 - s1)
					self.__k2 = 0.0
			tt = (self.__k1, self.__k2)
			self.__table.append(tt)

	def __fi(self, f1: float, f2: float) -> float:
		return f1 + self.Kmu * f2

	def __fbl(self, f1: float, f2: float) -> float:
		return f1 / self.__fi(f1, f2)

	def f1(self, s: float) -> float:
		if self.__IsTable:
			if s <= 0:
				return self.__table[0][0]
			if s >= 1:
				return self.__table[self.__TABLE_NODES - 1][0]
			i1: int = min(self.__TABLE_NODES - 2, int(s / self.__TABLE_DS))
			i2: int = i1 + 1
			m: float = (self.__TABLE_DS * i2 - s) / self.__TABLE_DS
			return self.__table[i1][0] + m * (self.__table[i2][0] - self.__table[i1][0])
		else:
			if s <= self.__swmin:
				return 0.0
			if s >= self.__swmax:
				return self.__k1
			return self.__k1 * np.power((s - self.__swmin) / (self.__swmax - self.__swmin), self.__n1)

	def f2(self, s: float) -> float:
		if self.__IsTable:
			if s <= 0:
				return self.__table[0][1]
			if s >= 1:
				return self.__table[self.__TABLE_NODES - 1][1]
			i1: int = min(self.__TABLE_NODES - 2, int(s / self.__TABLE_DS))
			i2: int = i1 + 1
			m: float = (self.__TABLE_DS * i2 - s) / self.__TABLE_DS
			return self.__table[i1][1] + m * (self.__table[i2][1] - self.__table[i1][1])
		else:
			if s <= self.__swmin:
				return self.__k2
			if s >= self.__swmax:
				return 0.0
			return self.__k2 * np.power(1.0 - (s - self.__swmin) / (self.__swmax - self.__swmin), self.__n2)

	def fi(self, s: float) -> float:
		return self.__fi(self.f1(s), self.f2(s))

	def fbl(self, s: float) -> float:
		return self.__fbl(self.f1(s), self.f2(s))

	def dfbl(self, s: float) -> float:
		if self.__IsTable:
			if s < 0.0:
				return 0.0
			if s > 1.0:
				return 0.0
			i1: int = min(self.__TABLE_NODES - 2, int(s / self.__TABLE_DS))
			i2: int = i1 + 1
			f1: float = self.__table[i1][0]
			f2: float = self.__table[i1][1]
			fbl1: float = self.__fbl(f1, f2)
			f1: float = self.__table[i2][0]
			f2: float = self.__table[i2][1]
			fbl2: float = self.__fbl(f1, f2)
			return (fbl2 - fbl1) / self.__TABLE_DS
		else:
			if s <= self.__swmin:
				return 0.0
			if s >= self.__swmax:
				return 0.0
			ss: float = (s - self.__swmin) / (self.__swmax - self.__swmin)
			df1: float = self.__k1 * self.__n1 * np.power(ss, self.__n1 - 1)
			dfi: float = df1 - self.Kmu * self.__k2 * self.__n2 * np.power(1.0 - ss, self.__n2 - 1)
			vfi = self.fi(s)
			vf1 = self.f1(s)
			return (df1 * vfi - vf1 * dfi) / (vfi * vfi)
