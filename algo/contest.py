# номер посылки: 117450756
def main(robot: list[int], limit: int) -> int:
    robot.sort()
    left, right = 0, len(robot) - 1
    count: int = 0

    while left <= right:
        if robot[left] + robot[right] <= limit:
            left += 1
        right -= 1
        count += 1

    return count


if __name__ == '__main__':
    robot = input()
    limit = int(input())
    array = robot.split()
    data_a = list(map(int, array))
    result = main(data_a, limit)
    print(result)
