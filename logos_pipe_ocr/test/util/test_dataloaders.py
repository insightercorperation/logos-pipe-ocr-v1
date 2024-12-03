import unittest
import os
from logos_pipe_ocr.util.dataloaders import ImageLoader, PromptLoader, EvalDataLoader, ModelConfigLoader

class TestImageLoader(unittest.TestCase):
    def setUp(self):
        self.valid_image_path = './data/image'  # 실제 이미지 경로로 변경
        self.empty_image_path = './data/empty_image'
        self.empty_dir_path = './data/empty_dir'
        os.makedirs(self.empty_image_path, exist_ok=True)  # 테스트를 위한 디렉토리 생성
        os.makedirs(self.empty_dir_path, exist_ok=True)  # 테스트를 위한 디렉토리 생성
    
    def tearDown(self):
        os.rmdir(self.empty_image_path)  # 빈 디렉토리 삭제
        os.rmdir(self.empty_dir_path)  # 빈 디렉토리 삭제

    def test_image_loader(self):
        # 유효한 이미지 로더 테스트
        image_loader = ImageLoader(self.valid_image_path)
        self.assertIsInstance(image_loader, ImageLoader)
        self.assertGreater(len(image_loader), 0)

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            ImageLoader('invalid/path/to/images')
    
    def test_empty_directory(self):
        with self.assertRaises(FileNotFoundError):
            ImageLoader(self.empty_dir_path)

    def test_empty_directory_with_unsupported_extension(self):
        open(os.path.join(self.empty_image_path, 'image.txt'), 'wb').close()  # 빈 이미지 파일 생성
        with self.assertRaises(FileNotFoundError):
            ImageLoader(self.empty_dir_path)
        os.remove(os.path.join(self.empty_image_path, 'image.txt'))  # 빈 이미지 파일 삭제
    
    def test_empty_file(self):
        open(os.path.join(self.empty_image_path, 'empty_image.png'), 'wb').close()  # 빈 이미지 파일 생성
        with self.assertRaises(FileNotFoundError):
            ImageLoader(self.empty_image_path)
        os.remove(os.path.join(self.empty_image_path, 'empty_image.png'))  # 빈 이미지 파일 삭제


class TestPromptLoader(unittest.TestCase):
    def setUp(self):
        self.valid_prompt_path = './data/prompt/prompt.txt'  # 실제 프롬프트 파일 경로로 변경
        self.empty_file_path = 'empty_prompt.txt'
        self.unsupported_file_path = 'prompt.csv'  # 지원되지 않는 파일 경로 추가
        open(self.empty_file_path, 'w').close()  # 빈 파일 생성
        open(self.unsupported_file_path, 'w').close()  # unsupported 파일 생성

    def tearDown(self):
        os.remove(self.empty_file_path)  # 빈 파일 삭제
        os.remove(self.unsupported_file_path)  # unsupported 파일 삭제

    def test_prompt_loader(self):
        # 유효한 프롬프트 로더 테스트
        with open(self.valid_prompt_path, 'w') as f:
            f.write("This is a test prompt.")
        prompt_loader = PromptLoader(self.valid_prompt_path)
        self.assertIsInstance(prompt_loader, PromptLoader)
        self.assertIsNotNone(prompt_loader.get_prompt())
        
    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            PromptLoader('invalid/path/to/prompt.txt')

    def test_unsupported_extension(self):
        with self.assertRaises(ValueError):
            PromptLoader(self.unsupported_file_path)

    def test_empty_file(self):
        with self.assertRaises(ValueError):
            PromptLoader(self.empty_file_path)


class TestEvalDataLoader(unittest.TestCase):
    def setUp(self):
        """테스트를 위한 초기 설정."""
        self.label_dir = 'test_dir/label'  # 테스트 레이블 디렉토리
        self.output_dir = 'test_dir/output'  # 테스트 출력 디렉토리
        
        # 테스트 디렉토리 및 파일 생성
        os.makedirs(self.label_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 테스트 레이블 파일 생성
        with open(os.path.join(self.label_dir, 'label1.json'), 'w') as f:
            f.write('{}')
        with open(os.path.join(self.label_dir, 'label2.json'), 'w') as f:
            f.write('{}')
        
        # 테스트 출력 파일 생성
        with open(os.path.join(self.output_dir, 'label1.json'), 'w') as f:
            f.write('output1')
        
    def tearDown(self):
        """테스트 후 정리 작업."""
        # 생성된 파일 및 디렉토리 삭제
        for dir_path in [self.label_dir, self.output_dir]:
            if os.path.exists(dir_path):
                for file in os.listdir(dir_path):
                    os.remove(os.path.join(dir_path, file))
                os.rmdir(dir_path)
        # test_dir 삭제
        if os.path.exists('test_dir'):
            os.rmdir('test_dir')  # test_dir 삭제

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            EvalDataLoader('invalid/path/to/label', 'invalid/path/to/output')

    def test_eval_data_loader(self):
        """EvalDataLoader의 기본 기능 테스트."""
        loader = EvalDataLoader(self.label_dir, self.output_dir)
        self.assertEqual(len(loader), 1)  # 레이블 파일과 출력 파일이 하나만 있어야 함
        
        label_paths = loader.get_label_file_paths()
        output_paths = loader.get_output_file_paths()
        
        self.assertEqual(len(label_paths), len(output_paths))  # 레이블 파일과 출력 파일이 쌍으로 존재해야 함
        self.assertIn(os.path.join(self.label_dir, 'label1.json'), label_paths)
        self.assertIn(os.path.join(self.output_dir, 'label1.json'), output_paths)

class TestModelConfigLoader(unittest.TestCase):
    def setUp(self):
        self.valid_config_path = './data/model_config/config.json'  # 실제 구성 파일 경로로 변경
        self.empty_file_path = 'empty_config.json'
        self.unsupported_file_path = 'config.txt'  # 지원되지 않는 파일 경로 추가
        open(self.empty_file_path, 'w').close()  # 빈 파일 생성
        open(self.unsupported_file_path, 'w').close()  # unsupported 파일 생성

    def tearDown(self):
        os.remove(self.empty_file_path)  # 빈 파일 삭제
        os.remove(self.unsupported_file_path)  # unsupported 파일 삭제

    def test_model_config_loader(self):
        # 유효한 모델 구성 로더 테스트
        model_config_loader = ModelConfigLoader(self.valid_config_path)
        self.assertIsInstance(model_config_loader, ModelConfigLoader)
        self.assertIsNotNone(model_config_loader.get_config())

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            ModelConfigLoader('invalid/path/to/config.yaml')

    def test_unsupported_extension(self):
        with self.assertRaises(ValueError):
            ModelConfigLoader(self.unsupported_file_path)

    def test_empty_file(self):
        with self.assertRaises(ValueError):
            ModelConfigLoader(self.empty_file_path)

if __name__ == '__main__':
    unittest.main()
