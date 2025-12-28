import json
import argparse
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PerformanceMetrics:
    """Класс для хранения метрик производительности"""
    frame_number: int
    cpu_fps: float
    cpu_time_ms: float
    gpu_fps: float
    gpu_time_ms: float
    cpu_rendering_time_ms: float
    culling_gpu_time_ms: float
    build_depth_pyramid_gpu_time_ms: float
    late_culling_gpu_time_ms: float
    gpu_rendering_time_ms: float
    gpu_models_time_ms: float
    gpu_shading_time_ms: float
    triangles_per_second: float
    triangles_per_second_millions: float
    triangles_number: int
    vertexes_number: int

    @classmethod
    def from_dict(cls, data: dict) -> 'PerformanceMetrics':
        """Создает экземпляр класса из словаря"""
        return cls(
            frame_number=data['frame_number'],
            cpu_fps=data['cpu_fps'],
            cpu_time_ms=data['cpu_time_ms'],
            gpu_fps=data['gpu_fps'],
            gpu_time_ms=data['gpu_time_ms'],
            cpu_rendering_time_ms=data['cpu_rendering_time_ms'],
            culling_gpu_time_ms=data['culling_gpu_time_ms'],
            build_depth_pyramid_gpu_time_ms=data['build_depth_pyramid_gpu_time_ms'],
            late_culling_gpu_time_ms=data['late_culling_gpu_time_ms'],
            gpu_rendering_time_ms=data['gpu_rendering_time_ms'],
            gpu_models_time_ms=data['gpu_models_time_ms'],
            gpu_shading_time_ms=data['gpu_shading_time_ms'],
            triangles_per_second=data['triangles_per_second'],
            triangles_per_second_millions=data['triangles_per_second_millions'],
            triangles_number=data['triangles_number'],
            vertexes_number=data['vertexes_number']
        )


def parse_json_file(filename: str) -> List[PerformanceMetrics]:
    """
    Парсит файл с последовательными JSON объектами.
    Игнорирует незавершенные JSON структуры в конце файла.
    
    Args:
        filename: Путь к файлу
        
    Returns:
        Список объектов PerformanceMetrics
    """
    metrics_list = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_json = ""
    brace_count = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Пропускаем пустые строки
        if not stripped:
            continue
        
        # Добавляем строку к текущему JSON объекту
        current_json += line
        
        # Считаем открывающие и закрывающие скобки
        brace_count += stripped.count('{') - stripped.count('}')
        
        # Если скобки сбалансированы, пытаемся распарсить
        if brace_count == 0 and current_json.strip():
            try:
                obj = json.loads(current_json)
                
                if isinstance(obj, dict):
                    try:
                        metrics = PerformanceMetrics.from_dict(obj)
                        metrics_list.append(metrics)
                    except (KeyError, TypeError) as e:
                        print(f"Ошибка при создании объекта: {e}")
                        print(f"Проблемный JSON: {current_json[:100]}...")
                        
            except json.JSONDecodeError as e:
                # Игнорируем ошибки парсинга (незавершенные объекты)
                pass
            
            # Сбрасываем для следующего объекта
            current_json = ""
    
    return metrics_list


def calculate_statistics(metrics: List[PerformanceMetrics], without_culling: bool = False):
    """
    Вычисляет статистику по метрикам
    
    Args:
        metrics: Список метрик
        without_culling: Если True, вычитает culling_gpu_time_ms из gpu_time_ms
    """
    print(f"Успешно распарсено записей: {len(metrics)}")
    
    if not metrics:
        print("Нет данных для обработки")
        return

    print(f"Количество треугольников: {metrics[0].triangles_number}")
    
    # Отбрасываем 10% первых и 5% последних значений
    total_count = len(metrics)
    start_idx = int(total_count * 0.10)
    end_idx = int(total_count * 0.95)
    
    filtered_metrics = metrics[start_idx:end_idx]
    
    print(f"\nВсего записей: {total_count}")
    print(f"Используется для расчетов: {len(filtered_metrics)} (без {start_idx} первых и {total_count - end_idx} последних)")
    
    if without_culling:
        print("\n⚠️  РЕЖИМ: GPU time без учёта времени culling")
    
    if not filtered_metrics:
        print("Недостаточно данных после фильтрации")
        return
    
    # Получаем GPU times с учётом флага
    if without_culling:
        gpu_times = [m.gpu_time_ms - m.culling_gpu_time_ms for m in filtered_metrics]
    else:
        gpu_times = [m.gpu_time_ms for m in filtered_metrics]
    
    avg_gpu_time = sum(gpu_times) / len(gpu_times)
    
    # Медиана
    sorted_times = sorted(gpu_times)
    n = len(sorted_times)
    if n % 2 == 0:
        median_gpu_time = (sorted_times[n//2 - 1] + sorted_times[n//2]) / 2
    else:
        median_gpu_time = sorted_times[n//2]
    
    # Стандартное отклонение
    variance = sum((t - avg_gpu_time) ** 2 for t in gpu_times) / len(gpu_times)
    std_dev_gpu_time = variance ** 0.5
    
    # Дополнительная статистика
    min_gpu_time = min(gpu_times)
    max_gpu_time = max(gpu_times)
    
    print(f"\nСтатистика GPU Time (ms):")
    print(f"Среднее: {avg_gpu_time:.2f}")
    print(f"Медиана: {median_gpu_time:.2f}")
    print(f"Стандартное отклонение: {std_dev_gpu_time:.2f}")
    print(f"Минимум: {min_gpu_time:.2f}")
    print(f"Максимум: {max_gpu_time:.2f}")
    
    # Средние значения culling time для справки
    avg_culling = sum(m.culling_gpu_time_ms for m in filtered_metrics) / len(filtered_metrics)
    print(f"\nСправка - среднее время culling (вычтено): {avg_culling:.2f} ms")

    avg_occlusion_culling = sum(m.late_culling_gpu_time_ms + m.build_depth_pyramid_gpu_time_ms
                                for m in filtered_metrics) / len(filtered_metrics)
    print(f"\nСправка - среднее время occlusion culling (вычтено): {avg_occlusion_culling:.2f} ms")



def main():
    parser = argparse.ArgumentParser(
        description='Парсер метрик производительности из JSON файла'
    )
    parser.add_argument(
        'filename',
        nargs='?',
        default='stats.json',
        help='Путь к JSON файлу (по умолчанию: stats.json)'
    )
    parser.add_argument(
        '--without-culling-time',
        action='store_true',
        help='Вычесть время culling из GPU time перед расчётами'
    )
    
    args = parser.parse_args()
    
    # Парсим файл
    metrics = parse_json_file(args.filename)
    
    # Вычисляем статистику
    calculate_statistics(metrics, without_culling=args.without_culling_time)


if __name__ == "__main__":
    main()
